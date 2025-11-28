# 🌿 道法自然

![repo size](https://img.shields.io/github/repo-size/xinetzone/tao.svg)
[![PyPI][pypi-badge]][pypi-link]
[![GitHub issues][issue-badge]][issue-link]
[![GitHub forks][fork-badge]][fork-link]
![atom star](https://gitcode.com/flexloop/flexloop/star/badge.svg)
[![GitHub stars][star-badge]][star-link]
[![GitHub license][license-badge]][license-link]
[![contributors][contributor-badge]][contributor-link]
[![watcher][watcher-badge]][watcher-link]
[![Binder][binder-badge]][binder-link]
[![Downloads][download-badge]][download-link]
[![Documentation Status][status-badge]][status-link]
[![PyPI - Downloads][install-badge]][install-link]

[pypi-badge]: https://img.shields.io/pypi/v/taolib.svg
[pypi-link]: https://pypi.org/project/taolib/
[issue-badge]: https://img.shields.io/github/issues/xinetzone/tao
[issue-link]: https://github.com/xinetzone/tao/issues
[fork-badge]: https://img.shields.io/github/forks/xinetzone/tao
[fork-link]: https://github.com/xinetzone/tao/network
[star-badge]: https://img.shields.io/github/stars/xinetzone/tao
[star-link]: https://github.com/xinetzone/tao/stargazers
[license-badge]: https://img.shields.io/github/license/xinetzone/tao
[license-link]: https://github.com/xinetzone/tao/LICENSE
[contributor-badge]: https://img.shields.io/github/contributors/xinetzone/tao
[contributor-link]: https://github.com/xinetzone/tao/contributors
[watcher-badge]: https://img.shields.io/github/watchers/xinetzone/tao
[watcher-link]: https://github.com/xinetzone/tao/watchers
[binder-badge]: https://mybinder.org/badge_logo.svg
[binder-link]: https://mybinder.org/v2/gh/xinetzone/tao/main
[install-badge]: https://img.shields.io/pypi/dw/taolib?label=pypi%20installs
[install-link]: https://pypistats.org/packages/taolib
[status-badge]: https://readthedocs.org/projects/taolib/badge/?version=latest
[status-link]: https://taolib.readthedocs.io/zh-cn/latest/?badge=latest
[download-badge]: https://pepy.tech/badge/taolib
[download-link]: https://pepy.tech/project/taolib

## 以终为始

- [ ] 以数学、物理、化学、编程、英语、大模型为主题逐步展开知识记录以及应用。
- [ ] 搭建开源友好的知识传播平台。

## 安装

- 环境要求：`Python >= 3.10`
- 从 PyPI 安装：

```sh
pip install taolib
```

- 从源码安装（可用于开发与本地调试）：

```sh
git clone https://gitcode.com/flexloop/flexloop.git
cd flexloop
pip install -e .
```

可选：安装开发与文档相关依赖：

```sh
pip install -e "[doc,dev]"
```

## 使用说明

详细 API 与示例代码：
- [RTD 在线文档](https://taolib.readthedocs.io/zh-cn/latest/)。
- 或者在本地构建并查看文档：
    ```sh
    pip install -e .[doc]
    python -m invoke doc.clean
    python -m invoke doc
    ```
    生成的 HTML 文档将在 `doc/_build/html` 目录下。


## 问题与反馈

- 提交 [Issue](https://gitcode.com/flexloop/flexloop/issues)
- 参与[讨论](https://gitcode.com/flexloop/flexloop/discussions)与改进，欢迎提出建议或 [PR](https://gitcode.com/flexloop/flexloop/pulls)。

## 贡献

- Fork 仓库并创建分支（如 `feature/<topic>` 或 `fix/<issue>`）。
- 保持代码风格与类型检查通过，补充必要测试与文档。
- 提交 PR 时说明动机、改动点、影响范围与验证方式。

## 维护者

- [xinetzone@github](https://github.com/xinetzone) / [flexloop@atomgit](https://gitcode.com/flexloop/flexloop)

## 使用许可

- 许可证信息请查看 `LICENSE` 文件。
