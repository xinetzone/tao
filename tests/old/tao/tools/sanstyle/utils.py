from pathlib import Path

def rename_suffix(root, old, new):
    '''批量修改文件后缀'''
    root = Path(root)
    for path in root.rglob(f'*{old}'):
        new_name = path.name.split(old)[0]+new
        path.rename(path.parent/new_name)