# PowerShell 环境摩擦案例

本文档记录在 Windows/PowerShell 环境下执行命令时遇到的常见问题及解决方案。

---

## 一、Python `-c` 多行字符串截断

### 现象

在 PowerShell 中使用 `python -c "多行字符串"` 时，字符串被意外截断或解析错误。

### 原因

PowerShell 对引号内的换行符处理与 Bash 不同，多行字符串在传递给 Python 前可能被截断或转义。

### 解决方案

**方案 A**：使用独立 Python 脚本文件

```powershell
# 不推荐
python -c "
import os
print(os.getcwd())
"

# 推荐
python script.py
```

**方案 B**：使用 Write 工具或 Python 写入文件

```python
# 在 AI 助手中使用 Write 工具
Write("script.py", content)
```

---

## 二、Heredoc 语法不支持

### 现象

在 PowerShell 中使用 `cat <<'EOF'` 或 `<<EOF` 语法报错。

### 原因

PowerShell 不支持 Bash 风格的 heredoc 语法。

### 解决方案

**方案 A**：使用 Python 写入文件

```python
content = """多行内容"""
open("file.txt", "w", encoding="utf-8").write(content)
```

**方案 B**：使用 `@"..."@` here-string（PowerShell 原生）

```powershell
$content = @"
多行内容
"@
$content | Out-File -Encoding utf8 file.txt
```

---

## 三、Git commit message 编码乱码

### 现象

使用 `git commit -m "中文消息"` 后，commit message 显示为乱码。

### 原因

PowerShell 默认编码与 Git 期望的 UTF-8 不一致。

### 解决方案

**方案 A**：使用 `git commit -F <file>`

```powershell
# 1. 用 Python 写入 commit message 文件
python -c "open('commit-msg.txt', 'w', encoding='utf-8').write('docs: 中文提交信息')"

# 2. 使用 -F 参数
git commit -F commit-msg.txt

# 3. 清理临时文件
Remove-Item commit-msg.txt
```

**方案 B**：设置 PowerShell 编码

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:LC_ALL = "C.UTF-8"
```

---

## 四、文件路径中的反斜杠转义

### 现象

在 Python 字符串中使用 Windows 路径时，反斜杠被误解析为转义字符。

### 原因

Python 字符串中 `\` 是转义字符，`\t`、`\n` 等会被特殊处理。

### 解决方案

**方案 A**：使用原始字符串 `r"..."`

```python
path = r"d:\spaces\AgentForge\file.txt"
```

**方案 B**：使用双反斜杠

```python
path = "d:\\spaces\\AgentForge\\file.txt"
```

**方案 C**：使用正斜杠（Python 3 兼容）

```python
path = "d:/spaces/AgentForge/file.txt"
```

---

## 五、命令输出编码乱码

### 现象

运行 Python 脚本后，输出的中文显示为乱码。

### 原因

文件写入时未显式指定 UTF-8 编码。

### 解决方案

**始终显式指定编码**

```python
# 写入文件
with open("file.txt", "w", encoding="utf-8") as f:
    f.write("中文内容")

# 读取文件
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

---

## 最佳实践总结

| 场景 | 推荐方案 |
|------|----------|
| 多行字符串 | Write 工具 > 独立 .py 脚本 > Python -c |
| Git commit | `git commit -F <file>` > `-m` 参数 |
| 文件路径 | 原始字符串 `r"..."` 或正斜杠 |
| 文件读写 | 始终指定 `encoding='utf-8'` |
| 编码问题 | 写入后立即回读验证 |

---

**来源**：`tech-debt-governance-checklist.md` §7 PowerShell 环境摩擦治理。本会话中多次遇到 PowerShell 相关问题，收敛为上述解决方案。

*文档版本 v1.0 | 2026-06-21*
