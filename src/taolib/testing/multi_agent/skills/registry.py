"""技能注册表。

管理技能的注册、查询和加载。
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type

from taolib.testing.multi_agent.errors import SkillError
from taolib.testing.multi_agent.skills.protocols import BaseSkill, Skill


class SkillRegistry:
    """技能注册表。"""

    def __init__(self):
        """初始化技能注册表。"""
        self._skills: Dict[str, Skill] = {}
        self._skill_classes: Dict[str, Type[Skill]] = {}
        self._skill_paths: Dict[str, Path] = {}

    def register_skill(self, skill: Skill) -> None:
        """注册技能实例。

        Args:
            skill: 技能实例

        Raises:
            SkillError: 技能已存在
        """
        if skill.id in self._skills:
            raise SkillError(f"Skill with id '{skill.id}' already registered")

        self._skills[skill.id] = skill

    def register_skill_class(self, skill_class: Type[Skill]) -> None:
        """注册技能类。

        Args:
            skill_class: 技能类

        Raises:
            SkillError: 技能类已存在
        """
        # 获取技能ID（需要实例化）
        try:
            temp_skill = skill_class.__new__(skill_class)
            skill_id = getattr(temp_skill, "id", None)
        except Exception:
            skill_id = None

        if skill_id is None:
            # 尝试从类名推断
            skill_id = skill_class.__name__.lower().replace("skill", "")

        if skill_id in self._skill_classes:
            raise SkillError(f"Skill class with id '{skill_id}' already registered")

        self._skill_classes[skill_id] = skill_class

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """获取技能实例。

        Args:
            skill_id: 技能ID

        Returns:
            Optional[Skill]: 技能实例,如果不存在则返回None
        """
        return self._skills.get(skill_id)

    def get_skill_class(self, skill_id: str) -> Optional[Type[Skill]]:
        """获取技能类。

        Args:
            skill_id: 技能ID

        Returns:
            Optional[Type[Skill]]: 技能类,如果不存在则返回None
        """
        return self._skill_classes.get(skill_id)

    def create_skill(self, skill_id: str, **kwargs) -> Skill:
        """创建技能实例。

        Args:
            skill_id: 技能ID
            **kwargs: 技能初始化参数

        Returns:
            Skill: 创建的技能实例

        Raises:
            SkillError: 技能类不存在
        """
        skill_class = self.get_skill_class(skill_id)
        if skill_class is None:
            raise SkillError(f"Skill class '{skill_id}' not found")

        return skill_class(**kwargs)

    def get_all_skills(self) -> List[Skill]:
        """获取所有已注册的技能实例。

        Returns:
            List[Skill]: 技能实例列表
        """
        return list(self._skills.values())

    def get_all_skill_classes(self) -> Dict[str, Type[Skill]]:
        """获取所有已注册的技能类。

        Returns:
            Dict[str, Type[Skill]]: 技能类字典
        """
        return self._skill_classes.copy()

    def unregister_skill(self, skill_id: str) -> None:
        """注销技能。

        Args:
            skill_id: 技能ID
        """
        if skill_id in self._skills:
            del self._skills[skill_id]
        if skill_id in self._skill_classes:
            del self._skill_classes[skill_id]
        if skill_id in self._skill_paths:
            del self._skill_paths[skill_id]

    def load_skill_from_file(self, file_path: Path, skill_class_name: Optional[str] = None) -> str:
        """从文件加载技能。

        Args:
            file_path: 技能文件路径
            skill_class_name: 技能类名,如果为None则自动查找

        Returns:
            str: 加载的技能ID

        Raises:
            SkillError: 加载失败
        """
        if not file_path.exists():
            raise SkillError(f"Skill file not found: {file_path}")

        # 导入模块
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise SkillError(f"Failed to load skill from {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # 查找技能类
        skill_class = None
        if skill_class_name:
            skill_class = getattr(module, skill_class_name, None)
        else:
            # 自动查找继承自Skill的类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, Skill)
                    and obj is not Skill
                    and obj is not BaseSkill
                ):
                    skill_class = obj
                    break

        if skill_class is None:
            raise SkillError(f"No skill class found in {file_path}")

        # 注册技能类
        self.register_skill_class(skill_class)
        skill_id = next(
            (id for id, cls in self._skill_classes.items() if cls == skill_class),
            None,
        )

        if skill_id:
            self._skill_paths[skill_id] = file_path

        return skill_id or skill_class.__name__

    def load_skills_from_directory(self, directory: Path) -> List[str]:
        """从目录加载所有技能。

        Args:
            directory: 技能目录路径

        Returns:
            List[str]: 加载的技能ID列表
        """
        loaded_skills = []

        if not directory.exists():
            return loaded_skills

        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            try:
                skill_id = self.load_skill_from_file(file_path)
                loaded_skills.append(skill_id)
            except Exception as e:
                print(f"Failed to load skill from {file_path}: {e}")

        return loaded_skills

    def clear(self) -> None:
        """清空注册表。"""
        self._skills.clear()
        self._skill_classes.clear()
        self._skill_paths.clear()


# 全局注册表实例
_global_registry: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    """获取全局技能注册表。

    Returns:
        SkillRegistry: 技能注册表
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry()
    return _global_registry


def set_skill_registry(registry: SkillRegistry) -> None:
    """设置全局技能注册表。

    Args:
        registry: 技能注册表
    """
    global _global_registry
    _global_registry = registry
