"""工作流加载器测试。"""

from pathlib import Path

import pytest

from taolib.symphony.config.loader import WorkflowDefinition, load_workflow
from taolib.symphony.errors import WorkflowLoadError


class TestLoadWorkflow:
    """测试 load_workflow 解析逻辑。"""

    def test_parse_yaml_front_matter(self, tmp_path: Path) -> None:
        """正常解析 YAML 前置数据和正文。"""
        path = tmp_path / "WORKFLOW.md"
        path.write_text(
            "---\n"
            "tracker:\n"
            "  kind: linear\n"
            "  api_key: $LINEAR_API_KEY\n"
            "  project_slug: test-proj\n"
            "polling:\n"
            "  interval_ms: 5000\n"
            "---\n"
            "\n"
            "# My Prompt\n"
            "Hello world\n",
            encoding="utf-8",
        )
        wf = load_workflow(path)
        assert isinstance(wf, WorkflowDefinition)
        assert wf.config["tracker"]["kind"] == "linear"
        assert wf.config["tracker"]["project_slug"] == "test-proj"
        assert wf.config["polling"]["interval_ms"] == 5000
        assert "Hello world" in wf.prompt_template

    def test_no_front_matter(self, tmp_path: Path) -> None:
        """无 --- 时 config 为空映射，全文作为 prompt_template。"""
        path = tmp_path / "WORKFLOW.md"
        path.write_text("# Just a prompt\nNo front matter here.\n", encoding="utf-8")
        wf = load_workflow(path)
        assert wf.config == {}
        assert wf.prompt_template == "# Just a prompt\nNo front matter here."

    def test_invalid_yaml_not_a_map(self, tmp_path: Path) -> None:
        """YAML 前置数据不是映射时抛出 WorkflowLoadError。"""
        path = tmp_path / "WORKFLOW.md"
        path.write_text(
            "---\n"
            "- not\n"
            "- a\n"
            "- map\n"
            "---\n"
            "body\n",
            encoding="utf-8",
        )
        with pytest.raises(WorkflowLoadError):
            load_workflow(path)

    def test_empty_file(self, tmp_path: Path) -> None:
        """空文件应返回空配置和空模板。"""
        path = tmp_path / "WORKFLOW.md"
        path.write_text("", encoding="utf-8")
        wf = load_workflow(path)
        assert wf.config == {}
        assert wf.prompt_template == ""

    def test_front_matter_with_empty_body(self, tmp_path: Path) -> None:
        """有 YAML 前置数据但无正文。"""
        path = tmp_path / "WORKFLOW.md"
        path.write_text(
            "---\n"
            "tracker:\n"
            "  kind: linear\n"
            "---\n",
            encoding="utf-8",
        )
        wf = load_workflow(path)
        assert wf.config["tracker"]["kind"] == "linear"
        assert wf.prompt_template == ""
