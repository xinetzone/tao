#!/usr/bin/env python
import os
import sys

REQUIRED_ENTRIES = [
    '.temp/',
    '.archive/',
    'docs/_build/',
    '__pycache__/',
    '*.pyc',
    '.venv/',
    'venv/',
    '.idea/',
    '.vscode/',
    '*.swp',
    '*.swo',
    '.DS_Store',
    'Thumbs.db',
]

EXPECTED_DIRS = [
    ('.temp/', 'temporary files'),
    ('.archive/', 'archived projects'),
    ('docs/_build/', 'Sphinx build output'),
    ('__pycache__/', 'Python bytecode cache'),
    ('.venv/', 'virtual environment'),
]

def check_gitignore():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(repo_root, '.git')):
        repo_root = os.path.dirname(repo_root)
        if repo_root == '/':
            print('ERROR: Not inside a git repository')
            return False
    
    gitignore_path = os.path.join(repo_root, '.gitignore')
    
    if not os.path.exists(gitignore_path):
        print('ERROR: .gitignore not found')
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_entries = []
    for entry in REQUIRED_ENTRIES:
        if entry not in content:
            missing_entries.append(entry)
    
    if missing_entries:
        print('FAIL: .gitignore is missing required entries:')
        for entry in missing_entries:
            print(f'  - {entry}')
        print()
        print('Suggested fix: Add these entries to .gitignore')
        return False
    else:
        print('PASS: .gitignore contains all required entries')
    
    for dir_path, desc in EXPECTED_DIRS:
        full_path = os.path.join(repo_root, dir_path)
        if os.path.exists(full_path):
            print(f'INFO: Found {desc}: {dir_path}')
    
    return True

def main():
    print('=== .gitignore Monthly Audit ===')
    print()
    
    if check_gitignore():
        print()
        print('All checks passed!')
        sys.exit(0)
    else:
        print()
        print('Some checks failed. Please review and fix.')
        sys.exit(1)

if __name__ == '__main__':
    main()
