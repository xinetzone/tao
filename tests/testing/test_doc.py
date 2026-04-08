"""doc.py 模块单元测试。"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from invoke.collection import Collection
from invoke.context import Context

from taolib.testing.doc import (
    ProjectConfig,
    ProjectConfigValidator,
    _build_sphinx_opts,
    _get_sphinx_paths,
    _make_project_namespace,
    build,
    build_parallel,
    clean,
    create_docs,
    multi_sites,
    sites,
)


class TestGetSphinxPaths(unittest.TestCase):
    """测试 _get_sphinx_paths 函数。"""

    def test_default_values(self) -> None:
        """测试默认值。"""
        ctx = Context()
        source, target = _get_sphinx_paths(ctx, None, None)
        self.assertEqual(source, "doc")
        self.assertEqual(target, "doc/_build/html")

    def test_custom_values(self) -> None:
        """测试自定义值。"""
        ctx = Context()
        source, target = _get_sphinx_paths(ctx, "custom_src", "custom_target")
        self.assertEqual(source, "custom_src")
        self.assertEqual(target, "custom_target")

    def test_context_config(self) -> None:
        """测试从上下文读取配置。"""
        ctx = Context()
        ctx.sphinx = MagicMock()
        ctx.sphinx.source = "ctx_source"
        ctx.sphinx.target = "ctx_target"
        source, target = _get_sphinx_paths(ctx, None, None)
        self.assertEqual(source, "ctx_source")
        self.assertEqual(target, "ctx_target")


class TestClean(unittest.TestCase):
    """测试 clean 任务。"""

    def test_clean_nonexistent_directory(self) -> None:
        """测试清理不存在的目录。"""
        ctx = Context()
        ctx.sphinx = MagicMock()
        ctx.sphinx.target = "/nonexistent/path"
        clean(ctx)

    def test_clean_existing_directory(self) -> None:
        """测试清理存在的目录。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "_build"
            target_dir.mkdir()
            (target_dir / "test.txt").write_text("test")

            ctx = Context()
            ctx.sphinx = MagicMock()
            ctx.sphinx.target = str(target_dir)
            clean(ctx)

            self.assertFalse(target_dir.exists())


class TestBuild(unittest.TestCase):
    """测试 build 任务。"""

    @patch("invoke.context.Context.run")
    def test_build_default_params(self, mock_run: MagicMock) -> None:
        """测试默认参数构建。"""
        ctx = Context()
        ctx.sphinx = MagicMock()
        ctx.sphinx.source = "doc"
        ctx.sphinx.target = "doc/_build/html"
        mock_run.return_value = None

        build(ctx)

        # 验证 ctx.run 被调用了一次
        mock_run.assert_called_once()
        # 验证调用参数包含 sphinx.cmd.build
        call_args = mock_run.call_args
        self.assertIn("sphinx.cmd.build", call_args[0][0])
        self.assertIn("doc", call_args[0][0])
        self.assertIn("doc/_build/html", call_args[0][0])

    @patch("invoke.context.Context.run")
    def test_build_with_language(self, mock_run: MagicMock) -> None:
        """测试带语言参数的构建。"""
        ctx = Context()
        ctx.sphinx = MagicMock()
        ctx.sphinx.source = "doc"
        ctx.sphinx.target = "doc/_build/html"
        mock_run.return_value = None

        build(ctx, language="en")

        # 验证 ctx.run 被调用了一次
        mock_run.assert_called_once()
        # 验证调用参数包含 language 设置
        call_args = mock_run.call_args
        self.assertIn("-D language=en", call_args[0][0])
        self.assertIn("doc/_build/html/en", call_args[0][0])


class TestCreateDocs(unittest.TestCase):
    """测试 create_docs 函数。"""

    def test_create_docs_single_project(self) -> None:
        """测试单项目配置。"""
        namespace = create_docs(source="doc", target="doc/_build/html")
        self.assertIsInstance(namespace, Collection)

    def test_create_docs_with_list(self) -> None:
        """测试列表形式的多项目配置。"""
        configs = [
            {"name": "project1", "source": "doc1", "target": "build1"},
            {"name": "project2", "source": "doc2", "target": "build2"},
        ]
        namespace = create_docs(configs)
        self.assertIsInstance(namespace, Collection)

    def test_create_docs_with_dict(self) -> None:
        """测试字典形式的多项目配置。"""
        configs = {
            "project1": {"source": "doc1", "target": "build1"},
            "project2": {"source": "doc2", "target": "build2"},
        }
        namespace = create_docs(configs)
        self.assertIsInstance(namespace, Collection)


class TestSites(unittest.TestCase):
    """测试 sites 函数。"""

    def test_sites_returns_collection(self) -> None:
        """测试 sites 返回 Collection。"""
        namespace = sites(source="doc", target="doc/_build/html")
        self.assertIsInstance(namespace, Collection)


class TestMultiSites(unittest.TestCase):
    """测试 multi_sites 函数。"""

    def test_multi_sites_returns_collection(self) -> None:
        """测试 multi_sites 返回 Collection。"""
        configs = {
            "project1": {"source": "doc1", "target": "build1"},
        }
        namespace = multi_sites(configs)
        self.assertIsInstance(namespace, Collection)


if __name__ == "__main__":
    unittest.main()


class TestProjectConfigValidator(unittest.TestCase):
    """测试 ProjectConfigValidator 类。"""

    def test_from_dict_with_all_fields(self) -> None:
        """测试从完整字典创建配置。"""
        data = {"name": "test", "source": "src", "target": "out", "children": "sub"}
        config = ProjectConfigValidator.from_dict(data)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.source, "src")
        self.assertEqual(config.target, "out")
        self.assertEqual(config.children, "sub")

    def test_from_dict_with_defaults(self) -> None:
        """测试从字典创建配置时使用默认值。"""
        data: dict[str, str] = {}
        config = ProjectConfigValidator.from_dict(data, index=5)
        self.assertEqual(config.name, "doc_6")
        self.assertEqual(config.source, "doc")
        self.assertEqual(config.target, "doc/_build/html")
        self.assertEqual(config.children, "")

    def test_from_dict_empty_name_raises(self) -> None:
        """测试空名称抛出 ValueError。"""
        data = {"name": ""}
        with self.assertRaises(ValueError):
            ProjectConfigValidator.from_dict(data)

    def test_from_dict_none_name_raises(self) -> None:
        """测试 None 名称抛出 ValueError。"""
        data = {"name": None}
        with self.assertRaises(ValueError):
            ProjectConfigValidator.from_dict(data)

    def test_normalize_from_dict(self) -> None:
        """测试 normalize 处理字典。"""
        config = ProjectConfigValidator.normalize({"name": "test"})
        self.assertIsInstance(config, ProjectConfig)
        self.assertEqual(config.name, "test")

    def test_normalize_from_projectconfig(self) -> None:
        """测试 normalize 返回相同的 ProjectConfig 实例。"""
        original = ProjectConfig(name="test", source="src")
        result = ProjectConfigValidator.normalize(original)
        self.assertIs(result, original)

    def test_normalize_invalid_type_raises(self) -> None:
        """测试不支持的类型抛出 TypeError。"""
        with self.assertRaises(TypeError):
            ProjectConfigValidator.normalize(123)


class TestMakeProjectNamespace(unittest.TestCase):
    """测试 _make_project_namespace 函数。"""

    def test_returns_collection(self) -> None:
        """测试返回 Collection 对象。"""
        config = ProjectConfig(name="test", source="doc", target="out")
        namespace = _make_project_namespace(config)
        self.assertIsInstance(namespace, Collection)
        self.assertEqual(namespace.name, "test")

    def test_configures_sphinx_paths(self) -> None:
        """测试配置正确的 sphinx 路径。"""
        config = ProjectConfig(name="mydoc", source="src", target="build")
        namespace = _make_project_namespace(config)
        # 验证配置被正确设置
        self.assertIn("doc", namespace.collections)


class TestProjectConfigDataClass(unittest.TestCase):
    """测试 ProjectConfig 数据类。"""

    def test_default_values(self) -> None:
        """测试默认值。"""
        config = ProjectConfig(name="test")
        self.assertEqual(config.source, "doc")
        self.assertEqual(config.target, "doc/_build/html")
        self.assertEqual(config.children, "")

    def test_custom_values(self) -> None:
        """测试自定义值。"""
        config = ProjectConfig(
            name="test", source="custom_src", target="custom_out", children="sub"
        )
        self.assertEqual(config.name, "test")
        self.assertEqual(config.source, "custom_src")
        self.assertEqual(config.target, "custom_out")
        self.assertEqual(config.children, "sub")


class TestCreateDocsWithProjectConfig(unittest.TestCase):
    """测试 create_docs 对 dict[str, ProjectConfig] 输入的处理。"""

    def test_create_docs_with_dict_of_projectconfig(self) -> None:
        """回归测试：dict[str, ProjectConfig] 输入不抛 TypeError。"""
        configs = {
            "project1": ProjectConfig(
                name="placeholder", source="doc1", target="build1"
            ),
            "project2": ProjectConfig(
                name="placeholder", source="doc2", target="build2"
            ),
        }
        namespace = create_docs(configs)
        self.assertIsInstance(namespace, Collection)


class TestBuildSphinxOpts(unittest.TestCase):
    """测试 _build_sphinx_opts 辅助函数。"""

    def test_default(self) -> None:
        """测试默认选项输出。"""
        opts, lang = _build_sphinx_opts("", None, False, "auto", True)
        self.assertEqual(opts, "-j auto --keep-going")
        self.assertIsNone(lang)

    def test_with_language(self) -> None:
        """测试 language 拼接 + 返回 lang_suffix。"""
        opts, lang = _build_sphinx_opts("", "en", False, "auto", False)
        self.assertIn("-D language=en", opts)
        self.assertEqual(lang, "en")

    def test_with_nitpick(self) -> None:
        """测试 nitpick 拼接。"""
        opts, lang = _build_sphinx_opts("", None, True, "auto", False)
        self.assertIn("-n -W -T", opts)
        self.assertIsNone(lang)

    def test_combined(self) -> None:
        """测试多选项组合。"""
        opts, lang = _build_sphinx_opts("-v", "zh", True, "4", True)
        self.assertIn("-v", opts)
        self.assertIn("-D language=zh", opts)
        self.assertIn("-n -W -T", opts)
        self.assertIn("-j 4", opts)
        self.assertIn("--keep-going", opts)
        self.assertEqual(lang, "zh")

    def test_no_keep_going(self) -> None:
        """测试 keep_going=False。"""
        opts, _ = _build_sphinx_opts("", None, False, "auto", False)
        self.assertNotIn("--keep-going", opts)


class TestBuildParallel(unittest.TestCase):
    """测试 build_parallel 函数。"""

    @patch("taolib.testing.doc._build_single_project")
    def test_success(self, mock_build: MagicMock) -> None:
        """测试全部成功构建。"""
        mock_build.return_value = ("src->out", True, "")
        configs = [
            ProjectConfig(name="p1", source="doc1", target="out1"),
            ProjectConfig(name="p2", source="doc2", target="out2"),
        ]
        results = build_parallel(configs, max_workers=1)
        self.assertEqual(len(results), 2)
        self.assertTrue(results["p1"])
        self.assertTrue(results["p2"])

    @patch("taolib.testing.doc._build_single_project")
    def test_partial_failure(self, mock_build: MagicMock) -> None:
        """测试部分项目失败。"""
        mock_build.side_effect = [
            ("doc1->out1", True, ""),
            ("doc2->out2", False, "ERROR: build failed"),
        ]
        configs = [
            ProjectConfig(name="ok", source="doc1", target="out1"),
            ProjectConfig(name="fail", source="doc2", target="out2"),
        ]
        results = build_parallel(configs, max_workers=1)
        self.assertTrue(results["ok"])
        self.assertFalse(results["fail"])

    def test_empty_input(self) -> None:
        """测试空列表返回空字典。"""
        results = build_parallel([])
        self.assertEqual(results, {})

    @patch("taolib.testing.doc._build_single_project")
    def test_dict_of_projectconfig(self, mock_build: MagicMock) -> None:
        """测试 dict[str, ProjectConfig] 输入。"""
        mock_build.return_value = ("src->out", True, "")
        configs = {
            "my_proj": ProjectConfig(name="placeholder", source="doc", target="out"),
        }
        results = build_parallel(configs, max_workers=1)
        self.assertEqual(len(results), 1)
        self.assertTrue(results["my_proj"])



