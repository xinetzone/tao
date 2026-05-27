"""验证 .agents/rules/ 规则文件完整性与交叉引用。"""

from pathlib import Path

RULES_DIR = Path(__file__).parent.parent / ".agents" / "rules"
BROWSER_AGENT_MD = RULES_DIR / "browser-agent.md"
DOCUMENTATION_MD = RULES_DIR / "documentation.md"


class TestBrowserAgentRuleFile:
    """验证 browser-agent.md 文件存在性与内容完整性。"""

    def test_file_exists(self):
        """规则文件必须存在。"""
        assert BROWSER_AGENT_MD.exists(), f"规则文件不存在：{BROWSER_AGENT_MD}"

    def test_file_not_empty(self):
        """规则文件内容不得为空。"""
        content = BROWSER_AGENT_MD.read_text(encoding="utf-8")
        assert content.strip(), "browser-agent.md 内容为空"

    def test_contains_temp_path_keyword(self):
        """.temp/ 路径规范必须出现在规则文件中。"""
        content = BROWSER_AGENT_MD.read_text(encoding="utf-8")
        assert ".temp/" in content, "browser-agent.md 缺少 .temp/ 路径关键词"

    def test_contains_screenshot_path_rule(self):
        """截图路径规范相关关键词必须存在。"""
        content = BROWSER_AGENT_MD.read_text(encoding="utf-8")
        assert "截图" in content, "browser-agent.md 缺少截图相关规则描述"

    def test_contains_wording_template(self):
        """措辞模板章节必须存在（内容提取指令）。"""
        content = BROWSER_AGENT_MD.read_text(encoding="utf-8")
        assert "措辞" in content or "模板" in content, (
            "browser-agent.md 缺少措辞模板相关内容"
        )

    def test_contains_explicit_path_instruction(self):
        """规则文件需明确要求显式指定截图输出路径。"""
        content = BROWSER_AGENT_MD.read_text(encoding="utf-8")
        assert "显式" in content or "explicit" in content.lower(), (
            "browser-agent.md 未包含显式路径指定要求"
        )


class TestDocumentationMdReferencesBrowserAgent:
    """验证 documentation.md 正确引用了 browser-agent.md。"""

    def test_documentation_md_exists(self):
        """documentation.md 必须存在。"""
        assert DOCUMENTATION_MD.exists(), f"文档治理规则文件不存在：{DOCUMENTATION_MD}"

    def test_documentation_references_browser_agent(self):
        """documentation.md 中必须包含对 browser-agent.md 的引用。"""
        content = DOCUMENTATION_MD.read_text(encoding="utf-8")
        assert "browser-agent.md" in content, (
            "documentation.md 未引用 browser-agent.md，交叉引用缺失"
        )

    def test_documentation_references_temp_screenshot_rule(self):
        """documentation.md 中的浏览器代理截图条款必须提及 .temp/ 路径。"""
        content = DOCUMENTATION_MD.read_text(encoding="utf-8")
        # 确认两条关键信息同时存在于文档中
        assert ".temp/" in content, "documentation.md 未提及 .temp/ 截图路径规则"
        assert "浏览器代理" in content or "browser" in content.lower(), (
            "documentation.md 未提及浏览器代理相关规则"
        )
