# Git 

## 统一 Git 在不同系统的行为

可以通过以下方法统一 Git 在不同系统的行为：

1. **设置 .gitattributes 文件**
```
* text=auto
*.sh eol=lf
*.py eol=lf
*.md eol=lf
```

2. **配置全局设置**
```bash
# 对所有用户统一换行符处理
git config --global core.autocrlf input
```

3. **文件类型处理**
```
# 二进制文件禁止差异比较
*.png binary
*.jpg binary
```

4. **权限保留**
```
# 保持可执行文件权限
*.sh eol=lf
*.py eol=lf
```

这些配置可确保不同操作系统开发者提交的代码不会因换行符差异产生文件变更。


```
name: Docker Image CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:

  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Build the Docker image
      run: docker build . --file Dockerfile --tag my-image-name:$(date +%s)
```