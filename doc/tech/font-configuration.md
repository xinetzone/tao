# 字体配置

`taolib.fonts` 负责把字体资源变成“确实能被渲染后端使用”的状态。字体是跨图表、文档、PDF 的通用资源，因此该子系统位于包顶层，而不是挂在某个绘图子包下；matplotlib 只是当前唯一的落地后端。

## 安装

matplotlib 不是 `taolib` 的强制依赖，核心发行版保持零依赖：

```bash
pip install "taolib[fonts]"
# 或
uv add "taolib[fonts]"
```

未安装 matplotlib 时，只有触及该后端的调用会失败，`import taolib.fonts` 本身不受影响。

## 快速开始

```python
from taolib.fonts import configure_matplotlib_fonts

# 注册目录内（含子目录）的字体，并把可解析的家族设为默认无衬线字体
resolved = configure_matplotlib_fonts("/path/to/fonts")

# 只用系统已安装字体，不注册新目录
configure_matplotlib_fonts(families=("Maple Mono NF CN", "Noto Sans CJK SC"))
```

`configure_matplotlib_fonts` 的返回值是**实际生效**的家族名元组（按入参顺序，只保留能解析的项），可直接用于日志或断言。

## 三道闸门

| 闸门 | 实现位置 | 判据 |
|---|---|---|
| 前置闸 | `discovery.iter_font_files` | 目录必须存在、是目录，且至少含一个 `.ttf/.otf/.ttc/.otc` 文件 |
| 注册闸 | `registry.register_font_directory` | 按规范化绝对路径去重，重复调用不会让 matplotlib 的字体列表持续膨胀 |
| 生效闸 | `matplotlib.configure_matplotlib_fonts` | 写入 `rcParams` 后用 `findfont(..., fallback_to_default=False)` 反查，解析不到任何家族即抛异常 |

关键设计：**写入成功不等于字体可用**。因此生效闸不把“rcParams 赋值完成”当作成功，而是反向解析验证；同时 `font.family` 固定为 `["sans-serif"]`，具体家族名写入 `font.sans-serif`，避免直接改 `font.family` 导致回退链失效。

## 参数与行为

| 参数 | 默认值 | 说明 |
|---|---|---|
| `font_directory` | `None` | `None` 表示不注册新目录，仅在已安装字体中查找 |
| `families` | `("Maple Mono NF CN",)` | 候选家族，按优先级排列 |
| `unicode_minus` | `False` | 是否用 U+2212 绘制负号；默认关闭，避免中文字体缺该码位时显示为方框 |

## 异常

所有故障统一归为 `FontConfigError`，便于调用方单点捕获：

| 触发条件 | 文案示例 |
|---|---|
| 未安装 matplotlib | 提示安装 `taolib[fonts]` |
| 目录不存在或不是目录 | `字体目录不存在或不是目录：…` |
| 目录中无字体文件 | `字体目录中没有字体文件：…` |
| 全部文件加载失败 | `字体目录中的字体全部加载失败：…` |
| 候选家族均不可解析 | `候选字体家族均无法解析：[…]` |

单个字体文件损坏不会中断整体流程：注册闸记录错误并跳过，最终由生效闸兜底判断是否还有可用家族。

## 扩展新后端

新增 reportlab、PIL、CSS `@font-face` 等目标时，在 `src/taolib/fonts/` 下新增同层模块，复用已有能力，无需改动既有模块：

```python
# src/taolib/fonts/reportlab.py（示例）
from .discovery import iter_font_files
from .registry import register_font_directory

def configure_reportlab_fonts(directory):
    register_font_directory(directory)  # 或直接用 iter_font_files 自行处理
    ...
```

随后在 `src/taolib/fonts/__init__.py` 中导出新的公开函数，即为唯一需要修改的公共入口。

## 模块分层

```
errors      异常类型
discovery   与后端无关的字体文件发现（前置闸）
registry    幂等注册到后端字体管理器（注册闸）
_deps       延迟导入垫片，供 registry 与后端模块共用
matplotlib  写 rcParams 并反查生效（生效闸）
```

依赖方向为无环 DAG：`errors ← discovery ← registry ← matplotlib`。下层不得反向依赖上层。

## 与旧实现的关系

字体能力曾在 `apps/chaos/old/` 快照中有一份同名实现，其默认字体路径指向不存在的目录、且以“写入成功”代替可用性校验。该实现已随唯一事实源原则移除，`taolib.fonts` 是当前唯一实现，不提供兼容层。