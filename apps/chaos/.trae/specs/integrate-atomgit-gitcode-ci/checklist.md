# Checklist

## AtomGit 平台兼容性
- [x] 项目配置文件中无 GitHub 绝对 URL 硬编码（或硬编码不影响 AtomGit 使用）
- [x] `.gitignore` 不包含 GitHub 特定路径
- [x] `.agents/` 中的规则文件不强制依赖 GitHub API
- [x] 可正常通过标准 Git 命令完成 clone/push/pull 操作

## GitCode CI 工作流
- [x] `.gitcode/workflows/ci.yml` 文件存在且语法正确
- [x] 工作流包含 `lint` 作业（ruff check 静态扫描）
- [x] 工作流包含 `test` 作业（pytest + coverage >= 80%）
- [x] 工作流包含 `build` 作业（uv build + artifact 上传）
- [x] 工作流使用 `euleros-2.10.1` runner
- [x] 工作流使用 GitCode 内置 `checkout-action` 和 `setup-python`
- [x] Python 版本指定为 `3.14`
- [x] 步骤中正确引用 `repo_workspace` 工作目录
- [x] 支持 push、pull_request、workflow_dispatch 三种触发方式
- [x] 作业间依赖关系正确（test 依赖 lint，build 依赖 test）

## 文档更新
- [x] 部署文档包含 AtomGit 平台使用指引
- [x] 部署文档包含 GitCode CI 触发规则与维护说明
- [x] 文档中包含从 AtomGit 克隆、推送的基础操作示例
