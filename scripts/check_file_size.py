#!/usr/bin/env python3
"""检查文件大小的 pre-commit 钩子"""
import sys
import os


def check_file_size(filenames):
    """检查文件大小，超过 10MB 的文件将被拒绝"""
    max_size = 10 * 1024 * 1024  # 10MB
    failed = False
    
    for filename in filenames:
        try:
            file_size = os.path.getsize(filename)
            if file_size > max_size:
                print(f"文件 {filename} 大小为 {file_size / (1024 * 1024):.2f}MB，超过 10MB 限制")
                failed = True
        except OSError as e:
            print(f"无法检查文件 {filename}: {e}")
            failed = True
    
    return failed


if __name__ == "__main__":
    sys.exit(check_file_size(sys.argv[1:]))
