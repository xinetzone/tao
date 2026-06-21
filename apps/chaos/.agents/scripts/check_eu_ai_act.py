"""EU AI Act Compliance Checker — 校验 Agent 配置是否符合 EU AI Act 要求

针对 EU AI Act 三条款（Art 12/14/15）的合规性校验：
- Article 12: 记录留存（Record-Keeping）
- Article 14: 人类监督（Human Oversight）
- Article 15: 鲁棒性（Robustness）

用法：
    uv run python .agents/scripts/check_eu_ai_act.py [OPTIONS]

选项：
    --constraints PATH    指定 constraints.toml 路径（默认自动查找）
    --agents-md PATH      指定 AGENTS.md 路径（默认自动查找）
    --verbose             显示详细校验信息
    --json                输出 JSON 格式报告
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Windows 终端 UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


# 状态常量（纯文本，避免编码问题）
STATUS_PASS = "PASS"  # 满足
STATUS_WARN = "WARN"  # 部分满足
STATUS_FAIL = "FAIL"  # 缺失
STATUS_SKIP = "SKIP"  # 不适用

# 严重级别
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"


@dataclass
class ComplianceCheck:
    """单个合规检查项。"""

    article: str  # "Art 12", "Art 14", "Art 15"
    requirement: str  # 要求描述
    constraint_key: str  # constraints.toml 中的键
    status: str  # "PASS", "WARN", "FAIL", "SKIP"
    details: str = ""  # 详细说明
    severity: str = SEVERITY_HIGH  # "high", "medium", "low"

    def get_status_display(self) -> str:
        """获取状态的显示文本。"""
        return {
            STATUS_PASS: "[OK] 满足",
            STATUS_WARN: "[WARN] 部分满足",
            STATUS_FAIL: "[FAIL] 缺失",
            STATUS_SKIP: "[SKIP] 不适用",
        }.get(self.status, "[?] 未知")

    def get_severity_display(self) -> str:
        """获取严重级别的显示文本。"""
        return {
            SEVERITY_HIGH: "[HIGH]",
            SEVERITY_MEDIUM: "[MED]",
            SEVERITY_LOW: "[LOW]",
        }.get(self.severity, "[?]")


@dataclass
class ComplianceReport:
    """合规报告。"""

    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    failed: int = 0
    skipped: int = 0
    checks: list[ComplianceCheck] = field(default_factory=list)

    def add_check(self, check: ComplianceCheck) -> None:
        """添加检查项。"""
        self.checks.append(check)
        self.total_checks += 1
        if check.status == STATUS_PASS:
            self.passed += 1
        elif check.status == STATUS_WARN:
            self.warnings += 1
        elif check.status == STATUS_FAIL:
            self.failed += 1
        else:
            self.skipped += 1

    def get_compliance_score(self) -> int:
        """计算合规分数（0-100）。"""
        if self.total_checks == 0:
            return 0
        # 警告扣 50% 分，失败扣 100% 分，跳过不计入
        effective_checks = self.total_checks - self.skipped
        if effective_checks == 0:
            return 100
        score = (
            (self.passed * 100 + self.warnings * 50) / effective_checks
        )
        return int(score)


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


def load_constraints(constraints_path: Path) -> dict[str, Any]:
    """加载 constraints.toml 文件。"""
    if not constraints_path.exists():
        return {}

    try:
        return tomllib.loads(constraints_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] 解析 constraints.toml 失败: {e}")
        return {}


def check_article_12(strong: dict[str, Any]) -> list[ComplianceCheck]:
    """校验 Article 12: 记录留存。"""
    checks = []

    # 检查 1: 是否启用审计
    audit_enabled = strong.get("audit_all_actions", False)
    checks.append(
        ComplianceCheck(
            article="Art 12",
            requirement="所有 AI Agent 操作必须可审计",
            constraint_key="constraints.strong.audit_all_actions",
            status=STATUS_PASS if audit_enabled else STATUS_FAIL,
            details="已启用全量审计" if audit_enabled else "未启用审计功能",
            severity=SEVERITY_HIGH,
        )
    )

    # 检查 2: 审计日志保留期限
    retention_days = strong.get("audit_retention_days", 0)
    if audit_enabled:
        if retention_days >= 365:
            status = STATUS_PASS
            details = f"日志保留 {retention_days} 天（>= 365 天）"
        elif retention_days > 0:
            status = STATUS_WARN
            details = f"日志保留 {retention_days} 天（建议 >= 365 天）"
        else:
            status = STATUS_FAIL
            details = "未设置日志保留期限"
    else:
        status = STATUS_SKIP
        details = "审计未启用，保留期限检查跳过"

    checks.append(
        ComplianceCheck(
            article="Art 12",
            requirement="审计日志必须保留足够时长",
            constraint_key="constraints.strong.audit_retention_days",
            status=status,
            details=details,
            severity=SEVERITY_MEDIUM,
        )
    )

    return checks


def check_article_14(strong: dict[str, Any]) -> list[ComplianceCheck]:
    """校验 Article 14: 人类监督。"""
    checks = []

    # 检查 1: 是否定义高风险操作清单
    high_risk_actions = strong.get("require_human_approval_for", [])
    if isinstance(high_risk_actions, list) and len(high_risk_actions) > 0:
        status = STATUS_PASS
        details = f"已定义 {len(high_risk_actions)} 个高风险操作: {', '.join(high_risk_actions[:3])}{'...' if len(high_risk_actions) > 3 else ''}"
    else:
        status = STATUS_FAIL
        details = "未定义高风险操作清单"

    checks.append(
        ComplianceCheck(
            article="Art 14",
            requirement="高风险操作必须有显式人类审批节点",
            constraint_key="constraints.strong.require_human_approval_for",
            status=status,
            details=details,
            severity=SEVERITY_HIGH,
        )
    )

    # 检查 2: Agent 是否需要 Role 绑定
    agent_requires_role = strong.get("agent_requires_role", False)
    checks.append(
        ComplianceCheck(
            article="Art 14",
            requirement="Agent 必须通过 Role 进入规范性协作体系",
            constraint_key="constraints.strong.agent_requires_role",
            status=STATUS_PASS if agent_requires_role else STATUS_WARN,
            details="已启用 Role 绑定" if agent_requires_role else "未启用 Role 绑定（建议启用）",
            severity=SEVERITY_MEDIUM,
        )
    )

    # 检查 3: Task 是否需要 Mission 归属
    task_requires_mission = strong.get("task_requires_mission", False)
    checks.append(
        ComplianceCheck(
            article="Art 14",
            requirement="Task 必须归属于某个 Mission（可追溯性）",
            constraint_key="constraints.strong.task_requires_mission",
            status=STATUS_PASS if task_requires_mission else STATUS_WARN,
            details="已启用 Mission 归属" if task_requires_mission else "未启用 Mission 归属（建议启用）",
            severity=SEVERITY_MEDIUM,
        )
    )

    return checks


def check_article_15(strong: dict[str, Any]) -> list[ComplianceCheck]:
    """校验 Article 15: 鲁棒性。"""
    checks = []

    # 检查 1: 输入净化
    sanitize_input = strong.get("sanitize_llm_input", False)
    checks.append(
        ComplianceCheck(
            article="Art 15",
            requirement="所有用户输入必须在到达 LLM 前净化",
            constraint_key="constraints.strong.sanitize_llm_input",
            status=STATUS_PASS if sanitize_input else STATUS_FAIL,
            details="已启用输入净化" if sanitize_input else "未启用输入净化（存在 Prompt Injection 风险）",
            severity=SEVERITY_HIGH,
        )
    )

    # 检查 2: 速率限制
    rate_limit = strong.get("rate_limit_per_minute", 0)
    if rate_limit > 0:
        status = STATUS_PASS
        details = f"已设置速率限制: {rate_limit} 次/分钟"
    else:
        status = STATUS_WARN
        details = "未设置速率限制（建议设置）"

    checks.append(
        ComplianceCheck(
            article="Art 15",
            requirement="系统应具备速率限制机制",
            constraint_key="constraints.strong.rate_limit_per_minute",
            status=status,
            details=details,
            severity=SEVERITY_MEDIUM,
        )
    )

    return checks


def check_eu_ai_act_compliance(
    constraints_path: Path, verbose: bool = False
) -> ComplianceReport:
    """执行 EU AI Act 合规性校验。"""
    report = ComplianceReport()

    # 加载 constraints.toml
    data = load_constraints(constraints_path)
    if not data:
        print(f"[WARN] 未找到 constraints.toml 或文件为空: {constraints_path}")
        return report

    strong = data.get("constraints", {}).get("strong", {})

    if verbose:
        print(f"[INFO] 加载 constraints.toml: {constraints_path}")
        print(f"       - 强约束项: {len(strong)} 个\n")

    # Article 12 检查
    for check in check_article_12(strong):
        report.add_check(check)

    # Article 14 检查
    for check in check_article_14(strong):
        report.add_check(check)

    # Article 15 检查
    for check in check_article_15(strong):
        report.add_check(check)

    return report


def print_report(report: ComplianceReport, verbose: bool = False) -> None:
    """打印合规报告。"""
    print("\n" + "=" * 70)
    print("EU AI Act 合规性校验报告")
    print("=" * 70)

    # 按条款分组显示
    current_article = ""
    for check in report.checks:
        if check.article != current_article:
            current_article = check.article
            print(f"\n{check.article}")
            print("-" * 70)

        status_display = check.get_status_display()
        severity_display = check.get_severity_display()

        print(f"{status_display} {severity_display} {check.requirement}")
        if verbose or check.status in (STATUS_FAIL, STATUS_WARN):
            print(f"   键: {check.constraint_key}")
            print(f"   详情: {check.details}")

    # 总结
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    print(f"总检查项: {report.total_checks}")
    print(f"[OK] 通过: {report.passed}")
    print(f"[WARN] 警告: {report.warnings}")
    print(f"[FAIL] 失败: {report.failed}")
    if report.skipped > 0:
        print(f"[SKIP] 跳过: {report.skipped}")
    print(f"\n合规分数: {report.get_compliance_score()}/100")

    # 风险评估
    score = report.get_compliance_score()
    if score >= 90:
        risk_level = "[LOW] 低风险"
        recommendation = "系统符合 EU AI Act 主要要求，建议保持当前治理水平。"
    elif score >= 70:
        risk_level = "[MED] 中风险"
        recommendation = "系统存在部分合规差距，建议在 2026.8.2 前完成整改。"
    else:
        risk_level = "[HIGH] 高风险"
        recommendation = "系统存在严重合规缺陷，需立即启动整改计划。"

    print(f"风险等级: {risk_level}")
    print(f"建议: {recommendation}")
    print("=" * 70)


def print_json_report(report: ComplianceReport) -> None:
    """打印 JSON 格式报告。"""
    output = {
        "summary": {
            "total_checks": report.total_checks,
            "passed": report.passed,
            "warnings": report.warnings,
            "failed": report.failed,
            "skipped": report.skipped,
            "compliance_score": report.get_compliance_score(),
        },
        "checks": [
            {
                "article": check.article,
                "requirement": check.requirement,
                "constraint_key": check.constraint_key,
                "status": check.status,
                "status_display": check.get_status_display(),
                "details": check.details,
                "severity": check.severity,
            }
            for check in report.checks
        ],
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def main() -> int:
    """入口：运行 EU AI Act 合规性校验。"""
    import argparse

    parser = argparse.ArgumentParser(
        description="EU AI Act 合规性校验工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础校验
  uv run python .agents/scripts/check_eu_ai_act.py

  # 详细输出
  uv run python .agents/scripts/check_eu_ai_act.py --verbose

  # JSON 格式输出
  uv run python .agents/scripts/check_eu_ai_act.py --json
        """,
    )
    parser.add_argument(
        "--constraints",
        type=Path,
        help="指定 constraints.toml 路径（默认自动查找）",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细校验信息",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式报告",
    )

    args = parser.parse_args()

    # 查找 .agents 目录
    if args.constraints:
        constraints_path = args.constraints
    else:
        agents_dir = find_agents_dir(Path.cwd())
        if not agents_dir:
            print("[FAIL] 未找到 .agents/ 目录。请在项目根目录运行。")
            print("       提示: 使用 --constraints 参数指定 constraints.toml 路径")
            return 2
        constraints_path = agents_dir / "constraints.toml"

    # 执行校验
    report = check_eu_ai_act_compliance(constraints_path, verbose=args.verbose)

    # 输出报告
    if args.json:
        print_json_report(report)
    else:
        print_report(report, verbose=args.verbose)

    # 返回退出码
    if report.failed > 0:
        return 1
    elif report.warnings > 0:
        return 0  # 警告不视为失败
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
