"""constraints-check — 校验 .agents/constraints.toml 合规性

验证 Layer 2 操作性约束：强约束不可违反、弱约束提警告、Role 绑定文件是否存在。
这是"规范即代码"的体现——AgentForge 自己的 CI 第一个跑这个检查。
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


def find_agents_dir(start_path: Path) -> Path | None:
    """向上查找 .agents/ 目录。"""
    current = start_path.resolve()
    for _ in range(10):
        candidate = current / ".agents"
        if candidate.is_dir():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def check_constraints(constraints_path: Path, agents_dir: Path) -> tuple[int, list[str], list[str]]:
    """校验 constraints.toml。

    Returns:
        (errors, warnings): 错误数、错误列表、警告列表
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not constraints_path.exists():
        warnings.append(f"constraints.toml 未找到 ({constraints_path})——跳过 Layer 2 约束校验")
        return 0, errors, warnings

    try:
        data = tomllib.loads(constraints_path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"constraints.toml 解析失败: {e}")
        return 1, errors, warnings

    # 1. 校验 strong 约束
    strong = data.get("constraints", {}).get("strong", {})
    required_strong = [
        "agent_requires_role",
        "task_requires_mission",
        "workflow_owns_no_knowledge",
        "permission_scoped_to_role_or_agent",
        "handoff_explicit",
    ]
    for key in required_strong:
        if key not in strong:
            errors.append(f"缺少强约束: constraints.strong.{key}")
        elif not strong[key]:
            errors.append(f"强约束被禁用: constraints.strong.{key} = false（强约束不应为 false）")

    # 2. 校验 weak 约束
    weak = data.get("constraints", {}).get("weak", {})
    required_weak = [
        "team_requires_multiple_roles",
        "agent_cross_team",
        "memory_persistence",
    ]
    for key in required_weak:
        if key not in weak:
            warnings.append(f"缺少弱约束声明: constraints.weak.{key}")

    # 3. 校验 parallel 约束
    parallel = data.get("constraints", {}).get("parallel", {})
    if not parallel:
        warnings.append("缺少并行隔离约束: constraints.parallel")
    else:
        required_parallel = ["file_isolation", "module_boundary", "integration_serial", "conflict_strategy"]
        for key in required_parallel:
            if key not in parallel:
                warnings.append(f"缺少并行约束: constraints.parallel.{key}")

    # 4. 校验 Role 绑定的文件是否存在
    roles_dir = agents_dir / "roles"
    if roles_dir.is_dir():
        for role_file in roles_dir.glob("*.toml"):
            try:
                role_data = tomllib.loads(role_file.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"Role 文件解析失败: {role_file.name} - {e}")
                continue

            bindings = role_data.get("role", {}).get("bindings", {})
            role_name = role_data.get("role", {}).get("name", role_file.stem)

            # 校验 rules 绑定
            for rule in bindings.get("rules", []):
                rule_path = agents_dir / rule
                if not rule_path.exists():
                    errors.append(f"Role '{role_name}' 绑定规则不存在: {rule}")

            # 校验 references 绑定
            for ref in bindings.get("references", []):
                ref_path = agents_dir / ref
                if not ref_path.exists():
                    errors.append(f"Role '{role_name}' 绑定引用不存在: {ref}")

            # 检查 constraints 声明的规则
            role_constraints = role_data.get("role", {}).get("constraints", {})
            if role_constraints.get("rules_must_exist", False) and not bindings.get("rules"):
                warnings.append(f"Role '{role_name}' 声明 rules_must_exist=true 但未绑定任何规则")

    # 5. 校验 world.toml 中的 kernel 引用的文件
    world_toml = agents_dir / "world.toml"
    if world_toml.exists():
        try:
            world_data = tomllib.loads(world_toml.read_text(encoding="utf-8"))
        except Exception as e:
            warnings.append(f"world.toml 解析失败（跳过内核引用校验）: {e}")
        else:
            kernel = world_data.get("kernel", {})
            for rule in kernel.get("rules", []):
                rule_path = agents_dir / rule
                if not rule_path.exists():
                    errors.append(f"world.toml kernel.rules 引用不存在: {rule}")
            for ref in kernel.get("references", []):
                ref_path = agents_dir / ref
                if not ref_path.exists():
                    errors.append(f"world.toml kernel.references 引用不存在: {ref}")

    return len(errors), errors, warnings


def main() -> int:
    """入口：运行 constraints 校验。"""
    agents_dir = find_agents_dir(Path.cwd())
    if not agents_dir:
        print("❌ 未找到 .agents/ 目录。请在项目根目录运行。")
        return 2

    constraints_path = agents_dir / "constraints.toml"
    error_count, errors, warnings = check_constraints(constraints_path, agents_dir)

    # 输出警告
    for w in warnings:
        print(f"⚠️  {w}")

    # 输出错误
    for e in errors:
        print(f"❌ {e}")

    if errors:
        print(f"\n❌ 约束校验失败: {error_count} 个错误, {len(warnings)} 个警告")
        return 1
    elif warnings:
        print(f"\n✅ 约束校验通过（{len(warnings)} 个警告）")
        return 0
    else:
        print("\n✅ 所有约束校验通过")
        return 0


if __name__ == "__main__":
    sys.exit(main())
