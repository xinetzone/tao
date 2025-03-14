# Gitlab

## 配置 Gitlab Runner

参考：[Create and run your first GitLab CI/CD pipeline](http://git.xmic.com/help/ci/quick_start/index.md)

## FAQs

1. 报错 `ERROR: Job failed: prepare environment: Process exited with status 1. Check https://docs.gitlab.com/runner/shells/index.html#shell-profile-loading for more information`

    解决方法：注释掉 `~/.bash_logout` 和 `/home/gitlab-runner/.bash_logout` 中全部内容即可。
    也可以在 `.gitlab-ci.yml` 中添加如下内容进行测试：
    ```yaml
    name: TVM 工具链

    stages:
    - build
    # - test
    # - package
    # - deploy

    build-tvm:
    stage: build
    before_script:
        - unset BASH_ENV # 禁用 bash 环境变量继承
        - echo "清理临时文件..."
        - rm -rf ~/.bash_profile ~/.bashrc # 清除可能冲突的配置文件
    script:
        - echo "Hello, $GITLAB_USER_LOGIN!"
        - echo "正在克隆 TVM 仓库..."
    ```
    