# Task 4: Add Raw Source Topic Entrypoints And Validate The Structure

**Files:**
- Create: `.agents/docs/sources/python/README.md`
- Create: `.agents/docs/sources/podman/README.md`

- [ ] **Step 1: Create the raw source topic directories**

Run:
```bash
New-Item -ItemType Directory -Force `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\sources\python, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\sources\podman
```

- [ ] **Step 2: Write `sources/python/README.md`**

Create `.agents/docs/sources/python/README.md`:
```md
# Python Raw Sources

该目录用于存放 Python 官方文档摘录、网页抓取结果和整理前的工作底稿。

## 使用规则

- 保留原始来源链接
- 标注抓取时间和版本
- 整理完成后，在 `../../references/python/` 中创建精炼页面
```

- [ ] **Step 3: Write `sources/podman/README.md`**

Create `.agents/docs/sources/podman/README.md`:
```md
# Podman Raw Sources

该目录用于存放 Podman 官方文档摘录、网页抓取结果和整理前的工作底稿。

## 使用规则

- 保留原始来源链接
- 标注抓取时间和版本
- 整理完成后，在 `../../references/podman/` 中创建精炼页面
```

- [ ] **Step 4: Run diagnostics on the new Markdown files**

Check with the editor diagnostics tool for:

```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/python/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/python/package-index.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/podman/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/podman/command-cheatsheet.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/issue-patterns/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/issue-patterns/python-errors.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/issue-patterns/podman-errors.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/integrations/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/integrations/python-in-agentforge.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/integrations/podman-in-agentforge.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/sources/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/sources/python/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/sources/podman/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/reference-page-template.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Run a final tree check**

Run:
```bash
Get-ChildItem c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs -Recurse `
  | Where-Object { $_.FullName -match "references|issue-patterns|integrations|sources|templates" } `
  | Select-Object FullName
```

Expected: the final output includes all planned directories and files, with no unexpected extra locations outside `.agents/docs/`.

- [ ] **Step 6: Commit**

```bash
git add .agents/docs/sources .agents/docs/templates
git commit -m "docs: add source staging area and template for AI wiki"
```
