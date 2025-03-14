# Gitlab

## 配置 Gitlab Runner

参考：[Create and run your first GitLab CI/CD pipeline](http://git.xmic.com/help/ci/quick_start/index.md)

## FAQs

1. 报错 `ERROR: Job failed: prepare environment: Process exited with status 1. Check https://docs.gitlab.com/runner/shells/index.html#shell-profile-loading for more information`

    解决方法：注释掉 `~/.bash_logout` 和 `/home/gitlab-runner/.bash_logout` 中全部内容即可。
 
    