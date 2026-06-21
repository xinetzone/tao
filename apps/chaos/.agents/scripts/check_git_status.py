#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path

def get_git_status():
    repo_root = Path(__file__).parent
    while not (repo_root / '.git').exists():
        repo_root = repo_root.parent
        if repo_root == repo_root.parent:
            return None
    
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception:
        return None

def check_staged_files(threshold=5):
    status_lines = get_git_status()
    
    if status_lines is None:
        print('ERROR: Not in a git repository')
        return False
    
    staged_files = [line for line in status_lines if line and line[0] in 'MADRC']
    unstaged_files = [line for line in status_lines if line and line[0] in ' M!']
    untracked_files = [line for line in status_lines if line and line.startswith('??')]
    
    total_pending = len(staged_files) + len(unstaged_files) + len(untracked_files)
    
    print('=== Git Status Check ===')
    print(f'Staged files: {len(staged_files)}')
    print(f'Unstaged files: {len(unstaged_files)}')
    print(f'Untracked files: {len(untracked_files)}')
    print(f'Total pending: {total_pending}')
    print()
    
    if total_pending > threshold:
        print(f'WARNING: {total_pending} files pending, exceeds threshold ({threshold})')
        print('Consider committing your changes soon!')
        print()
        if staged_files:
            print('Staged files:')
            for line in staged_files[:10]:
                print(f'  {line}')
            if len(staged_files) > 10:
                print(f'  ... and {len(staged_files) - 10} more')
        return False
    else:
        print(f'OK: {total_pending} files pending (threshold: {threshold})')
        return True

def main():
    threshold = 5
    if len(sys.argv) > 1:
        try:
            threshold = int(sys.argv[1])
        except ValueError:
            pass
    
    check_staged_files(threshold)

if __name__ == '__main__':
    main()
