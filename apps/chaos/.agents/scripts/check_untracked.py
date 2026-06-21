#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

def check_untracked_files():
    repo_root = Path(__file__).parent
    while not (repo_root / '.git').exists():
        repo_root = repo_root.parent
        if repo_root == repo_root.parent:
            print('ERROR: Not in a git repository')
            return False
    
    try:
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        untracked = result.stdout.strip().split('\n') if result.stdout.strip() else []
        untracked = [f for f in untracked if f]
        
        print('=== Untracked Files Check ===')
        
        if untracked:
            print(f'FAIL: {len(untracked)} untracked files not in .gitignore:')
            for f in untracked[:20]:
                print(f'  - {f}')
            if len(untracked) > 20:
                print(f'  ... and {len(untracked) - 20} more')
            print()
            print('Recommendation: Add these files to .gitignore or commit them')
            return False
        else:
            print('OK: No untracked files outside .gitignore')
            return True
    
    except Exception as e:
        print(f'ERROR: {e}')
        return False

def main():
    success = check_untracked_files()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
