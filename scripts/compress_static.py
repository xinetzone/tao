#!/usr/bin/env python3
"""
压缩 Sphinx 文档静态资源的脚本

功能：
1. 压缩 CSS 文件
2. 压缩 JavaScript 文件
3. 压缩图片文件（可选）
"""

import os
import gzip
import argparse
from pathlib import Path
import subprocess

# 配置
DEFAULT_BUILD_DIR = "doc/_build/html"
DEFAULT_OUTPUT_DIR = "doc/_build/html_compressed"

def compress_file(input_path, output_path):
    """压缩单个文件"""
    try:
        with open(input_path, 'rb') as f_in:
            content = f_in.read()
        
        with gzip.open(output_path, 'wb', compresslevel=9) as f_out:
            f_out.write(content)
        
        return True
    except Exception as e:
        print(f"压缩文件 {input_path} 失败: {e}")
        return False

def compress_css(input_path, output_path):
    """压缩 CSS 文件"""
    try:
        # 使用 cssnano 压缩 CSS
        result = subprocess.run(
            ['npx', 'cssnano', str(input_path), '--output', str(output_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            print(f"压缩 CSS 文件 {input_path} 失败: {result.stderr}")
            # 回退到 gzip 压缩
            return compress_file(input_path, output_path)
    except Exception as e:
        print(f"压缩 CSS 文件 {input_path} 失败: {e}")
        # 回退到 gzip 压缩
        return compress_file(input_path, output_path)

def compress_js(input_path, output_path):
    """压缩 JavaScript 文件"""
    try:
        # 使用 terser 压缩 JavaScript
        result = subprocess.run(
            ['npx', 'terser', str(input_path), '--output', str(output_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            print(f"压缩 JavaScript 文件 {input_path} 失败: {result.stderr}")
            # 回退到 gzip 压缩
            return compress_file(input_path, output_path)
    except Exception as e:
        print(f"压缩 JavaScript 文件 {input_path} 失败: {e}")
        # 回退到 gzip 压缩
        return compress_file(input_path, output_path)

def compress_image(input_path, output_path):
    """压缩图片文件"""
    try:
        # 使用 imagemin 压缩图片
        result = subprocess.run(
            ['npx', 'imagemin', str(input_path), '--out-dir', str(output_path.parent)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"压缩图片文件 {input_path} 失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="压缩 Sphinx 文档静态资源")
    parser.add_argument(
        "--build-dir",
        default=DEFAULT_BUILD_DIR,
        help=f"构建输出目录（默认：{DEFAULT_BUILD_DIR}"
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"压缩输出目录（默认：{DEFAULT_OUTPUT_DIR}"
    )
    parser.add_argument(
        "--compress-images",
        action="store_true",
        help="是否压缩图片文件"
    )
    
    args = parser.parse_args()
    
    # 检查构建目录是否存在
    build_dir = Path(args.build_dir)
    if not build_dir.exists():
        print(f"错误：构建目录 {build_dir} 不存在")
        return 1
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 复制文件并压缩
    total_files = 0
    compressed_files = 0
    
    for root, dirs, files in os.walk(build_dir):
        # 计算相对路径
        rel_path = os.path.relpath(root, build_dir)
        if rel_path == '.':
            rel_path = ''
        
        # 创建输出目录
        output_root = output_dir / rel_path
        output_root.mkdir(exist_ok=True)
        
        for file in files:
            input_path = Path(root) / file
            output_path = output_root / file
            
            # 根据文件类型进行压缩
            if file.endswith('.css'):
                if compress_css(input_path, output_path):
                    compressed_files += 1
            elif file.endswith('.js'):
                if compress_js(input_path, output_path):
                    compressed_files += 1
            elif args.compress_images and file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                if compress_image(input_path, output_path):
                    compressed_files += 1
            else:
                # 复制其他文件
                try:
                    with open(input_path, 'rb') as f_in:
                        content = f_in.read()
                    with open(output_path, 'wb') as f_out:
                        f_out.write(content)
                    compressed_files += 1
                except Exception as e:
                    print(f"复制文件 {input_path} 失败: {e}")
            
            total_files += 1
    
    # 计算压缩前后的大小
    def get_dir_size(directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    original_size = get_dir_size(build_dir)
    compressed_size = get_dir_size(output_dir)
    
    # 计算压缩率
    if original_size > 0:
        compression_rate = (1 - compressed_size / original_size) * 100
    else:
        compression_rate = 0
    
    # 打印报告
    print("\n=== 静态资源压缩报告 ===")
    print(f"总文件数：{total_files}")
    print(f"成功压缩：{compressed_files}")
    print(f"原始大小：{original_size / (1024 * 1024):.2f} MB")
    print(f"压缩后大小：{compressed_size / (1024 * 1024):.2f} MB")
    print(f"压缩率：{compression_rate:.2f}%")
    
    return 0

if __name__ == "__main__":
    exit(main())
