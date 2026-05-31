# AutoAPI 友好的 Docstring 风格规范

> 适用范围：`src/taolib/` 下所有模块、类、函数与属性的文档字符串。
>
> 强制级别：**MUST**（CI 通过 `mise run docs-strict` / `sphinx-build -W --keep-going` 强制零警告）。
>
> 关联文档：人类版摘要见 [`docs/tech/contributing.md`](../../../../../docs/tech/contributing.md#docstring-风格规范autoapi-友好)。

---

## 1. 背景与动机

本项目使用 [sphinx-autoapi](https://sphinx-autoapi.readthedocs.io/) 通过**静态扫描** `src/taolib/` 自动生成 API 文档，无需导入包。这与传统 `sphinx.ext.autodoc` 行为不同：

- **autodoc**：动态导入模块、读运行时属性、依赖类 docstring 中的 `Attributes:` 段。
- **autoapi**：静态扫描 AST、对每个字段独立生成 `.. py:attribute::` 指令、不依赖运行时。

两种模式叠加（例如同时写 `Attributes:` 段又被 autoapi 静态扫描）会**双重声明**同一对象，触发 docutils 的 `duplicate object description` 警告，在 `sphinx-build -W` 下直接构建失败。

本规范用三条铁律 + 反例锁死所有已知警告来源。

---

## 2. 三条铁律

### 2.1 属性说明使用 PEP 257 内联 docstring

紧跟字段定义下方放置三引号字符串。AutoAPI 会识别该字符串为属性描述，并填充到 `.. py:attribute::` 指令的 body。

#### ✅ 正确

```python
class RequestedTokenStrategy(StrEnum):
    """调用方请求安装令牌时表达的策略意图。"""

    AUTO = "auto"
    """根据运行环境自动选择，不主动下发 ``X-GitHub-Stateless-S2S-Token`` 头。"""

    ENABLED = "enabled"
    """主动请求启用无状态 S2S 令牌。"""
```

```python
@dataclass(slots=True)
class GitHubAppSettings:
    """GitHub App 的全局配置聚合。

    本类是 GitHub App 子模块各组件读取运行时参数的唯一源头，
    推荐通过 :meth:`from_env` 加载。
    """

    app_id: str
    """GitHub App 的 App ID。"""

    installation_id: str
    """默认的安装实例 ID。"""
```

#### ❌ 错误（双重声明）

```python
@dataclass(slots=True)
class GitHubAppSettings:
    """GitHub App 的全局配置聚合。

    Attributes:
        app_id: GitHub App 的 App ID。
        installation_id: 默认的安装实例 ID。
    """

    app_id: str
    installation_id: str
```

```python
class RequestedTokenStrategy(StrEnum):
    """调用方策略。

    :ivar AUTO: 自动选择。
    :ivar ENABLED: 启用。
    """

    AUTO = "auto"
    ENABLED = "enabled"
```

#### 等价规则

- **MUST NOT** 在类 docstring 中使用 `Attributes:` 段。
- **MUST NOT** 在类 docstring 中使用 `:ivar X:` 字段列表。
- **MAY** 在类 docstring 中使用 `:meth:`、`:func:`、`:class:` 等交叉引用，这些不会触发重复声明。
- **类描述本身**保留：用于陈述类的整体语义、跨字段不变量、与其他类的关系。

### 2.2 inline literal 不能紧贴中文标点

docutils 仅承认 ASCII 空格与少量英文标点（`. , ; ! ? : ( ) [ ] { } < > " ' / \ -`）为 `` ``...`` `` 的合法 end-string。紧贴**中文标点**（`：`、`、`、`。`、`；`、`，`、`！`、`？`、`（`、`）`）将让 docutils 把后续大段文本当作 inline literal，最终产生：

```
WARNING: Inline literal start-string without end-string.
```

#### ✅ 正确

```rst
- ``GITHUB_APP_ID`` 必填，App ID。
- ``GITHUB_APP_TOKEN_STRATEGY`` 默认策略，取值 ``auto`` / ``enabled`` / ``disabled``，默认 ``auto``。
```

#### ❌ 错误

```rst
- ``GITHUB_APP_ID``（必填）：App ID。
- ``GITHUB_APP_TOKEN_STRATEGY`` (默认 ``auto``)：策略选择。
```

#### 修复策略

1. **优先扁平化**：把括号嵌套、冒号说明改写成短句，让字面量后紧跟 ASCII 空格。
2. **次选英文标点**：仅在风格允许时把中文冒号改为英文冒号。
3. **避免**：通过加 ASCII 空格让中文叙述显得割裂。

### 2.3 不要启用 `imported-members`

`taolib.github_app/__init__.py` 已通过 re-export 暴露子模块对象（`from .config import GitHubAppSettings` 等）。如果 `autoapi_options` 启用 `imported-members`，AutoAPI 会同时在 `taolib/github_app/index.html` 与 `taolib/github_app/config/index.html` 各生成一份完整对象描述，导致 100+ 重复条目。

#### ✅ `docs/conf.py` 基线配置

```python
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
]
```

#### ❌ 禁止

```python
autoapi_options = [
    ...,
    "imported-members",  # 与 re-export 风格冲突
]
```

---

## 3. 全量反例速查表

| 反例模式 | 触发警告 | 修复 |
| --- | --- | --- |
| 类 docstring 含 `Attributes:` 段 | duplicate object description | 移除该段，改用 PEP 257 内联 docstring |
| 类 docstring 含 `:ivar X:` 字段 | duplicate object description | 同上 |
| `` ``ENV`` (默认 ``X``)： `` | inline literal start-string without end-string | 扁平化句式，去除嵌套括号与中文冒号 |
| `` ``X``、``Y``、``Z`` `` 中文顿号串联 | 同上 | 改为 ` / ` 或英文逗号空格连接 |
| 启用 `imported-members` | duplicate object description | 从 `autoapi_options` 移除 |
| 在 `__init__.py` 中再次书写跨模块的 docstring 段落引用对象 | duplicate object description | 仅在原始定义模块写 docstring，`__init__` 仅做 re-export |

---

## 4. lint 落地建议

短期靠人工评审 + CI 拦截；中期可加入以下检测脚本（P2 行动项）：

```python
# .agents/scripts/check_autoapi_docstring.py（伪码）
import ast, pathlib, re

ATTRIBUTES_HEADER = re.compile(r"^\s*Attributes\s*:\s*$", re.M)
IVAR_FIELD = re.compile(r":ivar\s+\w+:")

def main():
    for py in pathlib.Path("src/taolib").rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        if ATTRIBUTES_HEADER.search(text) or IVAR_FIELD.search(text):
            print(f"[autoapi-style] {py}: 发现 Attributes/ivar 段，请改用 PEP 257 内联 docstring")
            raise SystemExit(1)

if __name__ == "__main__":
    main()
```

可挂载到 `pre-commit` 与 CI 的 lint job 中，与 `mise run docs-strict` 形成"语法层 + 渲染层"双重防护。

---

## 5. 历史背景

- 2026-05-22 提交 `0f0219d`：首次为 taolib 源码补充中文 docstring。
- 2026-05-22 提交 `8e6d5d6`：切换为 sphinx-autoapi 自动生成 API 文档。
- 2026-05-23 提交 `84ec066`：移除全部 `Attributes:` 段、扁平化 inline literal，将构建警告从 37 降到 0。
- 2026-05-23 提交 `1b1ec58` / `84f8daf`：归档复盘报告并标记 P1 行动项已完成。
- 2026-05-23 本规范成文，关闭 P0 行动项。

---

*维护者：AgentForge AI Agent*
*最后更新：2026-05-23*
