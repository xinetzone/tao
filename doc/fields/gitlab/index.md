# Gitlab

## 配置 Gitlab Runner

参考：[Create and run your first GitLab CI/CD pipeline](http://git.xmic.com/help/ci/quick_start/index.md)

测试demo:
```yaml


stages:
  - install-conda
  # - test
  # - package
  # - deploy

install-conda:
  stage: install-conda
  script:
    - echo "Hello, $GITLAB_USER_LOGIN!"
    - echo "配置 conda"
    - wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    - bash miniconda.sh -b -p $CI_PROJECT_DIR/conda
    - source $CI_PROJECT_DIR/conda/etc/profile.d/conda.sh
    - conda activate
    # 验证安装
    - conda --version
    # - echo "PATH=$PATH"  # 检查路径是否包含conda
    - cd apps/doc/release && conda env create -f base.yaml
    - conda activate py312
```

## FAQs

1. 报错 `ERROR: Job failed: prepare environment: Process exited with status 1. Check https://docs.gitlab.com/runner/shells/index.html#shell-profile-loading for more information`

    解决方法：注释掉 `~/.bash_logout` 和 `/home/gitlab-runner/.bash_logout` 中全部内容即可。
 
    