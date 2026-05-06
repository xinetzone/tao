"""Symphony 工作流加载器。

解析 WORKFLOW.md 文件，提取 YAML 前置数据和提示模板。
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

from taolib.symphony.errors import WorkflowLoadError


@dataclass(frozen=True)
class WorkflowDefinition:
    """解析后的工作流定义。

    Attributes:
        config: YAML 前置数据根对象（映射）。
        prompt_template: 前置数据之后的 Markdown 正文（已去除首尾空白）。
    """

    config: dict
    prompt_template: str


def load_workflow(path: Path) -> WorkflowDefinition:
    """从文件加载 WORKFLOW.md 定义。

    解析规则：
    - 如果文件以 ``---`` 开头，解析至下一个 ``---`` 为 YAML 前置数据。
    - 剩余内容为 prompt_template。
    - 如果没有前置数据，整个文件作为 prompt_template，config 为空映射。
    - YAML 前置数据必须解码为映射，否则抛出 WorkflowLoadError。

    Args:
        path: WORKFLOW.md 文件路径。

    Returns:
        解析后的 WorkflowDefinition。

    Raises:
        WorkflowLoadError: 文件无法读取或前置数据不是映射。
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"无法读取工作流文件: {path}"
        raise WorkflowLoadError(msg) from exc

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        # parts[0] 为 --- 之前的空串，parts[1] 为 YAML 前置数据，parts[2] 为正文
        if len(parts) < 3:
            msg = f"工作流文件格式错误: 未找到结束的 '---' 分隔符 ({path})"
            raise WorkflowLoadError(msg)

        yaml_text = parts[1]
        body = parts[2]
    else:
        yaml_text = ""
        body = raw

    # 解析 YAML 前置数据
    if yaml_text.strip():
        try:
            parsed = yaml.safe_load(yaml_text)
        except yaml.YAMLError as exc:
            msg = f"YAML 解析失败 ({path}): {exc}"
            raise WorkflowLoadError(msg) from exc

        if parsed is None:
            parsed = {}

        if not isinstance(parsed, dict):
            msg = (
                f"工作流前置数据必须是映射，实际类型为 {type(parsed).__name__} ({path})"
            )
            raise WorkflowLoadError(msg)

        config: dict = parsed
    else:
        config = {}

    prompt_template = body.strip()

    return WorkflowDefinition(config=config, prompt_template=prompt_template)
