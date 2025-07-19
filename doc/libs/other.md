# 其他资源

:::::{grid} 2 3 3 4
::::{grid-item}
:::{card}  Drogon 中国人自己的异步怪兽
:link: https://drogon.org/

Drogon 是基于 C++17/20 的 Http 应用框架，使用 Drogon 可以方便的使用 C++ 构建各种类型的 Web 应用服务端程序。

Drogon 的主要应用平台是 Linux，也支持 Mac OS、FreeBSD 和 Windows。
它的主要特点如下：

- 网络层使用基于epoll(macOS/FreeBSD下是kqueue)的非阻塞IO框架，提供高并发、高性能的网络IO。详细请见TFB Tests Results；
- 全异步编程模式；
- 支持Http1.0/1.1(server端和client端)；
- 基于template实现了简单的反射机制，使主程序框架、控制器(controller)和视图(view)完全解耦；
- 支持cookies和内建的session；
- 支持后端渲染，把控制器生成的数据交给视图生成Html页面，视图由CSP模板文件描述，通过CSP标签把C++代码嵌入到Html页面，由drogon的命令行工具在编译阶段自动生成C++代码并编译；
- 支持运行期的视图页面动态加载(动态编译和加载so文件)；
- 非常方便灵活的路径(path)到控制器处理函数(handler)的映射方案；
- 支持过滤器(filter)链，方便在控制器之前执行统一的逻辑(如登录验证、Http Method约束验证等)；
- 支持https(基于OpenSSL实现);
- 支持websocket(server端和client端);
- 支持Json格式请求和应答, 对Restful API应用开发非常友好;
- 支持文件下载和上传,支持sendfile系统调用；
- 支持gzip/brotli压缩传输；
- 支持pipelining；
- 提供一个轻量的命令行工具drogon_ctl，帮助简化各种类的创建和视图代码的生成过程；
- 基于非阻塞IO实现的异步数据库读写，目前支持PostgreSQL和MySQL(MariaDB)数据库；
- 基于线程池实现sqlite3数据库的异步读写，提供与上文数据库相同的接口；
- 支持ARM架构；
- 方便的轻量级ORM实现，支持常规的对象到数据库的双向映射操作；
- 支持插件，可通过配置文件在加载期动态拆装；
- 支持内建插入点的AOP
:::
::::


::::{grid-item}
:::{card}  Kore - 2万行代码的运维杀手
:link: https://drogon.org/

它的秘密在于预派生工作进程+无锁队列设计，把CPU利用率从35%拉到98%
:::
::::

::::{grid-item}
:::{card} 唐僧叨叨
:link: https://tsdaodao.com/

让企业轻松拥有自己的即时通讯

历时八年时间打造的运营级别的开源即时通讯聊天软件(WuKongIM提供通讯动力)
:::
::::

::::{grid-item}
:::{card} AI 工具集
:link: https://ai-bot.cn/

AI 工具集是一个基于 AI 技术的工具集合，它可以帮助你快速地生成各种类型的代码，包括前端、后端、数据库、测试等。
:::
::::

::::{grid-item}
:::{card} KSubdomain: 极速无状态子域名爆破工具
:link: https://github.com/boy-hack/ksubdomain

KSubdomain 是一款基于无状态技术的子域名爆破工具，带来前所未有的扫描速度和极低的内存占用。 告别传统工具的效率瓶颈，体验闪电般的 DNS 查询，同时拥有可靠的状态表重发机制，确保结果的完整性。KSubdomain 支持 Windows、Linux 和 macOS，是进行大规模DNS资产探测的理想选择。
:::
::::

::::{grid-item}
:::{card} ZoomEye-python
:link: https://github.com/knownsec/ZoomEye-python

ZoomEye 是一款网络空间搜索引擎，用户可以使用浏览器方式 https://www.zoomeye.org 搜索网络设备。

ZoomEye-python 是一款基于 ZoomEye API 开发的 Python 库，提供了 ZoomEye 命令行模式，同时也可以作为 SDK 集成到其他工具中。该库可以让技术人员更便捷地搜索、导出 ZoomEye 的数据。
:::
::::

::::{grid-item}
:::{card} 404星链计划
:link: https://github.com/knownsec/404StarLink

「404星链计划」是知道创宇 404 实验室于 2020 年 8 月开始的计划，主要目的是改善安全圈内工具庞杂、水平层次不齐、开源无人维护的多种问题，促进安全开源社区的发展；通过这种方式将不同安全领域研究人员与开源项目链接起来。

星链计划将不断地收集优秀的安全开源项目，对收录的项目提供技术支持，持续跟踪和展示项目的更新和动态，并建立了星链计划社区，社区用户可以通过星链展示板块探索自己感兴趣的项目，同时还可以在社区内快速为开源作者反馈问题。以此方式帮助开源项目成长，促进安全社区发展。
:::
::::
:::::
