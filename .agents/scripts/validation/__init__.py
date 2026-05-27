"""技能验证体系模块"""

import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

try:
    from .validate_references import run as validate_references
    from .validate_retro_feedback import run as validate_retro_feedback
    from .validate_skill_md import run as validate_skill_md
    from .validate_workbench import run as validate_workbench
except ImportError:
    from validate_references import run as validate_references
    from validate_retro_feedback import run as validate_retro_feedback
    from validate_skill_md import run as validate_skill_md
    from validate_workbench import run as validate_workbench

__all__ = [
    "validate_skill_md",
    "validate_workbench",
    "validate_retro_feedback",
    "validate_references",
]
