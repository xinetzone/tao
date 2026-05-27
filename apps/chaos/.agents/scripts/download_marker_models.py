"""
预下载 marker-pdf 所需模型脚本

功能：
    - 预下载 marker-pdf 所有依赖模型到本地缓存
    - 支持指定模型存储目录（便于团队共享）
    - 显示下载进度和磁盘占用

用法:
    python download_marker_models.py [options]

示例:
    # 下载到默认缓存目录
    python download_marker_models.py

    # 下载到指定共享目录（团队复用）
    python download_marker_models.py --cache-dir D:\\shared\\marker-models
"""

import argparse
import os
import sys


def download_models(cache_dir: str | None = None) -> dict:
    """
    触发 marker-pdf 模型下载。

    marker-pdf 在首次运行时会自动从 HuggingFace 下载模型。
    我们通过创建一个空白 PDF 的转换请求来触发所有模型的下载。
    """
    try:
        from marker.converters.pdf import PdfConverter  # noqa: F401
        from marker.models import create_model_dict
        from marker.settings import settings  # noqa: F401

        print("[信息] 初始化 marker-pdf 模型下载...")

        # 如果指定了自定义缓存目录，设置环境变量
        if cache_dir:
            os.environ["TRANSFORMERS_CACHE"] = cache_dir
            os.environ["HF_HOME"] = cache_dir
            print(f"[信息] 模型缓存目录: {cache_dir}")

        # 创建模型字典，这会触发所有模型的下载
        print("[下载] 开始下载模型（这可能需要 10-20 分钟）...")
        model_dict = create_model_dict()

        print("[完成] 所有模型下载完毕")
        return {"success": True, "models": list(model_dict.keys())}

    except ImportError:
        print("[错误] marker-pdf 未安装，请先运行:")
        print("  pip install marker-pdf --only-binary :all:")
        return {"success": False, "error": "marker-pdf not installed"}

    except Exception as e:
        print(f"[错误] 模型下载失败: {e}")
        return {"success": False, "error": str(e)}


def check_models_cached(cache_dir: str | None = None) -> dict:
    """检查哪些模型已经缓存"""
    try:
        from marker.models import create_model_dict

        if cache_dir:
            os.environ["TRANSFORMERS_CACHE"] = cache_dir
            os.environ["HF_HOME"] = cache_dir

        model_dict = create_model_dict()
        return {"success": True, "models": list(model_dict.keys())}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_cache_size(cache_dir: str | None = None) -> int:
    """计算缓存目录总大小"""
    target_dir = cache_dir or os.path.expanduser("~/.cache/huggingface")
    if not os.path.exists(target_dir):
        return 0

    total = 0
    for dirpath, _dirnames, filenames in os.walk(target_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total


def format_size(size_bytes: int) -> str:
    """格式化字节大小为人类可读格式"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def main():
    parser = argparse.ArgumentParser(description="预下载 marker-pdf 模型")
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="模型缓存目录（默认使用 HuggingFace 默认缓存）",
    )
    parser.add_argument(
        "--check-only", action="store_true", help="仅检查模型是否已缓存，不执行下载"
    )
    args = parser.parse_args()

    print("=" * 50)
    print("marker-pdf 模型管理工具")
    print("=" * 50)

    # 检查当前缓存大小
    current_size = get_cache_size(args.cache_dir)
    print(f"当前缓存大小: {format_size(current_size)}")

    if args.check_only:
        print("\n[检查] 验证模型缓存状态...")
        result = check_models_cached(args.cache_dir)
        if result["success"]:
            print(f"✅ 所有模型已就绪（共 {len(result['models'])} 个）:")
            for model in result["models"]:
                print(f"  - {model}")
        else:
            print(f"❌ 模型检查失败: {result.get('error', '未知错误')}")
        return

    # 执行下载
    print("\n[下载] 开始预下载模型...")
    print("提示：首次下载约需 3-4GB 磁盘空间\n")

    result = download_models(args.cache_dir)

    if result["success"]:
        new_size = get_cache_size(args.cache_dir)
        print(f"\n{'=' * 50}")
        print("下载完成报告")
        print(f"{'=' * 50}")
        print(f"下载模型数: {len(result['models'])}")
        print(f"缓存总大小: {format_size(new_size)}")
        print(f"新增大小: {format_size(new_size - current_size)}")
        print("\n✅ 模型已就绪，后续转换无需再等待下载")
    else:
        print("\n❌ 下载失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
