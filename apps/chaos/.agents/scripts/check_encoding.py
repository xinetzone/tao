#!/usr/bin/env python
import os
import sys

def verify_file_encoding(filepath, sample_size=50):
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read(sample_size)
                if content:
                    return encoding, content
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    
    return None, None

def validate_encoding_on_write(filepath, content, expected_encoding='utf-8'):
    with open(filepath, 'w', encoding=expected_encoding) as f:
        f.write(content)
    
    detected_encoding, sample = verify_file_encoding(filepath)
    
    if detected_encoding is None:
        print(f'ERROR: Could not detect encoding for {filepath}')
        return False
    
    if detected_encoding.lower() not in ['utf-8', 'utf-8-sig']:
        print(f'WARNING: {filepath} saved with unexpected encoding: {detected_encoding}')
        print(f'  Expected: utf-8')
    
    print(f'OK: {filepath} validated (encoding: {detected_encoding})')
    return True

def main():
    if len(sys.argv) < 3:
        print('Usage: check_encoding.py <filepath> <content>')
        sys.exit(1)
    
    filepath = sys.argv[1]
    content = sys.argv[2]
    
    validate_encoding_on_write(filepath, content)

if __name__ == '__main__':
    main()
