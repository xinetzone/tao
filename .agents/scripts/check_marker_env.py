"""
Windows + marker-pdf 环境兼容性检查脚本

功能：
    - 检查 Python 版本兼容性
    - 验证 Pillow 预编译 wheel 可用性
    - 检查磁盘空间和内存
    - 测试 HuggingFace 网络连通性
    - 生成检查报告和修复建议

用法:
    python check_marker_env.py [options]

退出码:
    0 - 环境完全就绪
    1 - 环境存在问题，需修复
"""

import argparse
import platform
import shutil
import subprocess
import sys
import urllib.request


def check_python_version() -> dict:
    """检查 Python 版本"""
    major, minor, micro, _, _ = sys.version_info
    version_str = f"{major}.{minor}.{micro}"

    # marker-pdf 要求 Python >= 3.10
    is_compatible = (major == 3 and minor >= 10) or major > 3

    return {
        "name": "Python 版本",
        "status": "通过" if is_compatible else "失败",
        "value": version_str,
        "required": ">= 3.10",
        "fix": None if is_compatible else "请升级 Python 到 3.10 或更高版本",
    }


def check_pip_wheel_availability() -> dict:
    """检查 Pillow 预编译 wheel 是否可用"""
    try:
        # 尝试查询 Pillow 的可用 wheel
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", "pillow"],
            capture_output=True, text=True, encoding="utf-8"
        )

        # 备选方案：直接尝试安装并回滚
        test_result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pillow", "--only-binary", ":all:",
             "--dry-run", "--quiet"],
            capture_output=True, text=True, encoding="utf-8"
        )

        is_ok = test_result.returncode == 0
        return {
            "name": "Pillow 预编译包",
            "status": "通过" if is_ok else "警告",
            "value": "可用" if is_ok else "可能需从源码编译",
            "required": "预编译 wheel 可用",
            "fix": None if is_ok else "安装 Visual Studio Build Tools 或使用 --only-binary :all: 参数",
        }
    except Exception as e:
        return {
            "name": "Pillow 预编译包",
            "status": "未知",
            "value": f"检查失败: {e}",
            "required": "预编译 wheel 可用",
            "fix": "请检查 pip 版本和网络连接",
        }


def check_marker_installed() -> dict:
    """检查 marker-pdf 是否已安装"""
    installed = shutil.which("marker_single") is not None
    return {
        "name": "marker-pdf 安装",
        "status": "通过" if installed else "未安装",
        "value": "已安装" if installed else "未找到",
        "required": "已安装",
        "fix": None if installed else "运行: pip install marker-pdf --only-binary :all:",
    }


def check_disk_space() -> dict:
    """检查磁盘空间（marker-pdf 模型约需 4GB）"""
    try:
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024 ** 3)
        is_ok = free_gb >= 5  # 至少 5GB

        return {
            "name": "磁盘空间",
            "status": "通过" if is_ok else "警告",
            "value": f"{free_gb:.1f} GB 可用",
            "required": ">= 5 GB（模型缓存）",
            "fix": None if is_ok else "请清理磁盘空间，确保至少 5GB 可用",
        }
    except Exception as e:
        return {
            "name": "磁盘空间",
            "status": "未知",
            "value": f"检查失败: {e}",
            "required": ">= 5 GB",
            "fix": "请手动检查磁盘空间",
        }


def check_memory() -> dict:
    """检查系统内存"""
    try:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024 ** 3)
        is_ok = total_gb >= 8  # 建议至少 8GB

        return {
            "name": "系统内存",
            "status": "通过" if is_ok else "警告",
            "value": f"{total_gb:.1f} GB",
            "required": ">= 8 GB（推荐）",
            "fix": None if is_ok else "内存较小，建议分批处理大 PDF 或关闭其他程序",
        }
    except ImportError:
        return {
            "name": "系统内存",
            "status": "跳过",
            "value": "未安装 psutil",
            "required": ">= 8 GB",
            "fix": "可选: pip install psutil",
        }


def check_huggingface_connectivity() -> dict:
    """测试 HuggingFace 网络连通性"""
    urls = [
        ("HuggingFace", "https://huggingface.co"),
        ("清华镜像", "https://pypi.tuna.tsinghua.edu.cn"),
    ]

    results = []
    for name, url in urls:
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(req, timeout=10) as resp:
                results.append(f"{name}: 可达 ({resp.status})")
        except Exception:
            results.append(f"{name}: 不可达")

    has_access = any("可达" in r for r in results)

    return {
        "name": "网络连通性",
        "status": "通过" if has_access else "警告",
        "value": "; ".join(results),
        "required": "HuggingFace 或镜像源可访问",
        "fix": None if has_access else "请配置代理或使用 HF-MIRROR 镜像",
    }


def check_os_compatibility() -> dict:
    """检查操作系统兼容性"""
    system = platform.system()
    is_windows = system == "Windows"

    return {
        "name": "操作系统",
        "status": "通过",
        "value": f"{system} {platform.release()}",
        "required": "Windows / Linux / macOS",
        "fix": None,
        "note": "Windows 用户注意使用 pip --only-binary 安装策略" if is_windows else None,
    }


def run_all_checks() -> list:
    """运行所有检查项"""
    checks = [
        check_os_compatibility(),
        check_python_version(),
        check_pip_wheel_availability(),
        check_marker_installed(),
        check_disk_space(),
        check_memory(),
        check_huggingface_connectivity(),
    ]
    return checks


def print_report(checks: list) -> int:
    """打印检查报告，返回退出码"""
    print("=" * 60)
    print("marker-pdf 环境兼容性检查报告")
    print("=" * 60)

    passed = 0
    warnings = 0
    failed = 0

    for check in checks:
        status = check["status"]
        icon = "✅" if status == "通过" else "⚠️" if status in ("警告", "未安装") else "❌"

        if status == "通过":
            passed += 1
        elif status in ("警告", "未安装"):
            warnings += 1
        else:
            failed += 1

        print(f"\n{icon} {check['name']}")
        print(f"   状态: {status}")
        print(f"   当前: {check['value']}")
        print(f"   要求: {check['required']}")

        if check.get("fix"):
            print(f"   修复: {check['fix']}")
        if check.get("note"):
            print(f"   提示: {check['note']}")

    print(f"\n{'=' * 60}")
    print(f"汇总: {passed} 通过 | {warnings} 警告 | {failed} 失败")
    print("=" * 60)

    if failed > 0:
        print("\n❌ 环境不满足要求，请先修复上述问题")
        return 1
    elif warnings > 0:
        print("\n⚠️ 环境基本可用，但存在警告项，建议优化")
        return 0
    else:
        print("\n✅ 环境完全就绪，可以执行 PDF 转换")
        return 0


def main():
    parser = argparse.ArgumentParser(description="marker-pdf 环境兼容性检查")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    args = parser.parse_args()

    checks = run_all_checks()

    if args.json:
        import json
        print(json.dumps(checks, ensure_ascii=False, indent=2))
        sys.exit(0)

    exit_code = print_report(checks)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
