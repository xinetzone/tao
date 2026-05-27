from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from .manifest_parser import FragmentManifest, WorldInfo


class ValidationLevel(IntEnum):
    """兼容性校验层级，按执行顺序递增。"""

    L1_KERNEL_COMPAT = 1
    L2_CONFLICTS = 2
    L3_DEPENDENCIES = 3
    L4_FILE_CONFLICTS = 4


@dataclass(frozen=True)
class ValidationError:
    """单个校验错误。"""

    level: ValidationLevel
    message: str
    detail: str = ""


@dataclass
class ValidationResult:
    """校验结果汇总。"""

    passed: bool = True
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _expand_caret(constraint: str) -> str:
    """将 ``^`` 约束转换为标准 specifier 字符串。

    Args:
        constraint: 已去除 ``^`` 前缀的版本约束，如 ``"1.2.3"``、``"0.2"``。

    Returns:
        等价的 ``SpecifierSet`` 字符串，如 ``">=1.2.3, <2.0.0"``。
    """
    parts = constraint.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0

    if len(parts) == 1:
        base = f"{major}.0.0"
    elif len(parts) == 2:
        base = f"{major}.{minor}.0"
    else:
        base = f"{major}.{minor}.{patch}"

    if major == 0:
        if minor == 0:
            upper = "0.1.0" if len(parts) <= 2 else f"0.0.{patch + 1}"
        else:
            upper = f"0.{minor + 1}.0"
    else:
        upper = f"{major + 1}.0.0"

    return f">={base}, <{upper}"


def _expand_tilde(constraint: str) -> str:
    """将 ``~`` 约束转换为标准 specifier 字符串。

    Args:
        constraint: 已去除 ``~`` 前缀的版本约束，如 ``"1.2.3"``、``"1.2"``。

    Returns:
        等价的 ``SpecifierSet`` 字符串，如 ``">=1.2.3, <1.3.0"``。
    """
    parts = constraint.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0

    if len(parts) == 1:
        base = f"{major}.0.0"
    elif len(parts) == 2:
        base = f"{major}.{minor}.0"
    else:
        base = f"{major}.{minor}.{patch}"

    upper = f"{major}.{minor + 1}.0"
    return f">={base}, <{upper}"


def matches_constraint(version_str: str, constraint: str) -> bool:
    """检查版本是否满足约束。

    支持 ``">=1.2.0"``、``"^1.2"``、``"~1.2"``、``"*"``、``"=1.2.3"``、
    ``">=1.0, <3.0"`` 等语法。缺省版本号（如 ``"1.2"``）等价于 ``"^1.2"``。

    Args:
        version_str: 待比较的版本号。
        constraint: 版本约束字符串。

    Returns:
        若版本满足约束则返回 ``True``，否则返回 ``False``。
    """
    if constraint == "*":
        return True

    stripped = constraint.strip()

    if stripped.startswith("^"):
        specifier = _expand_caret(stripped[1:])
        return Version(version_str) in SpecifierSet(specifier)

    if stripped.startswith("~"):
        specifier = _expand_tilde(stripped[1:])
        return Version(version_str) in SpecifierSet(specifier)

    # 缺省版本号等价于 ^ 约束（如 "1.2" → "^1.2"）
    if not any(op in stripped for op in (">=", "<=", ">", "<", "!=", "==", "=", ",")):
        specifier = _expand_caret(stripped)
        return Version(version_str) in SpecifierSet(specifier)

    # 标准 specifier
    return Version(version_str) in SpecifierSet(stripped)


def validate(
    manifest: FragmentManifest,
    world: WorldInfo,
    agents_dir: Path,
) -> ValidationResult:
    """执行四层兼容性校验。

    校验层级依次为：

    1. **L1 Kernel 兼容性**：检查 Fragment 的 ``kernel-compat`` 是否满足
       当前世界的 ``world.version``。
    2. **L2 Fragment 互斥**：检查待安装 Fragment 的 ``conflicts`` 是否与
       世界已安装 Fragment 冲突。
    3. **L3 依赖完整性**：检查 ``dependencies`` 是否均已在世界安装且版本
       满足约束。
    4. **L4 文件冲突**：检查 ``contents`` 中的文件/目录是否已在 ``agents_dir``
       中存在。

    Args:
        manifest: 待安装 Fragment 的 manifest。
        world: 当前世界的 world.toml 解析结果。
        agents_dir: 世界 ``.agents/`` 目录的绝对路径。

    Returns:
        包含校验结果、错误与警告的 :class:`ValidationResult` 实例。
    """
    errors: list[ValidationError] = []
    warnings: list[str] = []

    # L1 Kernel 兼容性
    if manifest.kernel_compat is not None:
        world_version = Version(world.version)
        min_v = Version(manifest.kernel_compat.min_version)
        max_v = Version(manifest.kernel_compat.max_version)
        if not (min_v <= world_version < max_v):
            errors.append(
                ValidationError(
                    level=ValidationLevel.L1_KERNEL_COMPAT,
                    message=(
                        f"Kernel version {world.version} is not compatible "
                        f"(requires >={manifest.kernel_compat.min_version}, "
                        f"<{manifest.kernel_compat.max_version})"
                    ),
                ),
            )

    # L2 Fragment 互斥
    installed_map = {f.name: f for f in world.fragments}
    for conflict_name, conflict_constraint in manifest.conflicts.items():
        installed = installed_map.get(conflict_name)
        if installed is not None:
            if conflict_constraint == "*" or matches_constraint(
                installed.version, conflict_constraint
            ):
                errors.append(
                    ValidationError(
                        level=ValidationLevel.L2_CONFLICTS,
                        message=(
                            f"Conflicts with installed fragment "
                            f"'{conflict_name}' (constraint: {conflict_constraint})"
                        ),
                    ),
                )

    # L3 依赖完整性
    for dep_name, dep_constraint in manifest.dependencies.items():
        installed = installed_map.get(dep_name)
        if installed is None:
            errors.append(
                ValidationError(
                    level=ValidationLevel.L3_DEPENDENCIES,
                    message=f"Required dependency '{dep_name}' is not installed",
                ),
            )
        elif not matches_constraint(installed.version, dep_constraint):
            errors.append(
                ValidationError(
                    level=ValidationLevel.L3_DEPENDENCIES,
                    message=(
                        f"Dependency '{dep_name}' version {installed.version} "
                        f"does not satisfy constraint '{dep_constraint}'"
                    ),
                ),
            )

    # L4 文件冲突
    all_paths: list[str] = (
        manifest.contents.rules
        + manifest.contents.skills
        + manifest.contents.scripts
        + manifest.contents.docs
        + manifest.contents.templates
    )
    for p in all_paths:
        target = agents_dir / p
        if target.exists():
            errors.append(
                ValidationError(
                    level=ValidationLevel.L4_FILE_CONFLICTS,
                    message=f"File conflict: '{p}' already exists at {target}",
                ),
            )

    return ValidationResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
