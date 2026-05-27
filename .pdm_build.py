import subprocess
import sys

def pdm_build_initialize(context):
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            cwd=context.root,
            check=True
        )
        version = result.stdout.strip().lstrip('v')
        
        if '-' in version:
            parts = version.split('-')
            if len(parts) >= 3:
                version = f"{parts[0]}.dev{parts[1]}+{parts[2]}"
        
        context.metadata.version = version
        
        version_file = context.root / "src" / "taolib" / "_version.py"
        if version_file.exists():
            version_file.write_text(f"__version__ = '{version}'\n")
            
    except Exception as e:
        context.metadata.version = "0.7.1"

def pdm_build_update_files(context, files):
    pdm_build_initialize(context)
    return files
