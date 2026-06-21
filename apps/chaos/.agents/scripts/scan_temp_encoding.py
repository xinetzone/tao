#!/usr/bin/env python
import os
import sys
from pathlib import Path

def detect_encoding(filepath):
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'big5', 'shift_jis', 'euc-jp', 'euc-kr', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                f.read()
                return encoding
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    
    return None

def scan_temp_directory(temp_dir='.temp'):
    repo_root = Path(__file__).parent
    while not (repo_root / '.git').exists():
        repo_root = repo_root.parent
        if repo_root == repo_root.parent:
            break
    
    temp_path = repo_root / temp_dir
    
    if not temp_path.exists():
        print(f'INFO: {temp_dir} does not exist')
        return True
    
    text_extensions = {'.txt', '.md', '.py', '.js', '.ts', '.json', '.xml', '.yaml', '.yml', '.html', '.css', '.csv', '.log'}
    
    issues = []
    scanned = 0
    
    for filepath in temp_path.rglob('*'):
        if filepath.is_file() and filepath.suffix.lower() in text_extensions:
            scanned += 1
            encoding = detect_encoding(filepath)
            
            if encoding is None:
                issues.append((str(filepath.relative_to(repo_root)), 'binary or unknown'))
            elif encoding.lower() not in ['utf-8', 'utf-8-sig']:
                issues.append((str(filepath.relative_to(repo_root)), encoding))
    
    print(f'=== .temp/ Encoding Scan ===')
    print(f'Scanned: {scanned} text files')
    print()
    
    if issues:
        print('WARNING: Non-UTF-8 files detected:')
        for path, enc in issues:
            print(f'  - {path} ({enc})')
        print()
        print('Recommendation: Re-save these files with UTF-8 encoding')
        return False
    else:
        print('OK: All text files are UTF-8 encoded')
        return True

def main():
    success = scan_temp_directory()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
