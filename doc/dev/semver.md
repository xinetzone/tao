# 语义化版本

详细信息见：[语义化版本](https://semver.org/lang/zh-CN/)

版本格式：`主版本号.次版本号.修订号`，版本号递增规则如下：
- 主版本号：当你做了不兼容的 API 修改，
- 次版本号：当你做了向下兼容的功能性新增，
- 修订号：当你做了向下兼容的问题修正。
先行版本号及版本编译信息可以加到“`主版本号.次版本号.修订号`”的后面，作为延伸。

在软件管理的领域里存在着被称作“依赖地狱”的死亡之谷，系统规模越大，加入的包越多，你就越有可能在未来的某一天发现自己已深陷绝望之中。

在依赖高的系统中发布新版本包可能很快会成为噩梦。如果依赖关系过高，可能面临版本控制被锁死的风险（必须对每一个依赖包改版才能完成某次升级）。而如果依赖关系过于松散，又将无法避免版本的混乱（假设兼容于未来的多个版本已超出了合理数量）。当你项目的进展因为版本依赖被锁死或版本混乱变得不够简便和可靠，就意味着你正处于依赖地狱之中。

作为这个问题的解决方案之一，SemVer 提议用一组简单的规则及条件来约束版本号的配置和增长。这些规则是根据（但不局限于）已经被各种封闭、开放源码软件所广泛使用的惯例所设计。为了让这套理论运作，你必须先有定义好的公共 API。这可能包括文档或代码的强制要求。无论如何，这套 API 的清楚明了是十分重要的。一旦你定义了公共 API，你就可以透过修改相应的版本号来向大家说明你的修改。考虑使用这样的版本号格式：`X.Y.Z`（`主版本号.次版本号.修订号`）修复问题但不影响 API 时，递增修订号；API 保持向下兼容的新增及修改时，递增次版本号；进行不向下兼容的修改时，递增主版本号。

称这套系统为“语义化的版本控制”，在这套约定下，版本号及其更新方式包含了相邻版本间的底层代码和修改内容的信息。

规则如下：
1. 使用语义化版本控制的软件必须（MUST）定义公共 API。该 API 可以在代码中被定义或出现于严谨的文档内。无论何种形式都应该力求精确且完整。
2. 标准的版本号必须（MUST）采用 X.Y.Z 的格式，其中 X、Y 和 Z 为非负的整数，且禁止（MUST NOT）在数字前方补零。X 是主版本号、Y 是次版本号、而 Z 为修订号。每个元素必须（MUST）以数值来递增。例如：1.9.1 -> 1.10.0 -> 1.11.0。
3. 标记版本号的软件发行后，禁止（MUST NOT）改变该版本软件的内容。任何修改都必须（MUST）以新版本发行。
4. 主版本号为零（0.y.z）的软件处于开发初始阶段，一切都可能随时被改变。这样的公共 API 不应该被视为稳定版。
5. `1.0.0` 的版本号用于界定公共 API 的形成。这一版本之后所有的版本号更新都基于公共 API 及其修改内容。
6. 修订号 Z（x.y.Z | x > 0）必须（MUST）在只做了向下兼容的修正时才递增。这里的修正指的是针对不正确结果而进行的内部修改。
7. 次版本号 Y（x.Y.z | x > 0）必须（MUST）在有向下兼容的新功能出现时递增。在任何公共 API 的功能被标记为弃用时也必须（MUST）递增。也可以（MAY）在内部程序有大量新功能或改进被加入时递增，其中可以（MAY）包括修订级别的改变。每当次版本号递增时，修订号必须（MUST）归零。
8. 主版本号 X（X.y.z | X > 0）必须（MUST）在有任何不兼容的修改被加入公共 API 时递增。其中可以（MAY）包括次版本号及修订级别的改变。每当主版本号递增时，次版本号和修订号必须（MUST）归零。
9. 先行版本号可以（MAY）被标注在修订版之后，先加上一个连接号再加上一连串以句点分隔的标识符来修饰。标识符必须（MUST）由 ASCII 字母数字和连接号 [0-9A-Za-z-] 组成，且禁止（MUST NOT）留白。数字型的标识符禁止（MUST NOT）在前方补零。先行版的优先级低于相关联的标准版本。被标上先行版本号则表示这个版本并非稳定而且可能无法满足预期的兼容性需求。范例：1.0.0-alpha、1.0.0-alpha.1、1.0.0-0.3.7、1.0.0-x.7.z.92。
10. 版本编译信息可以（MAY）被标注在修订版或先行版本号之后，先加上一个加号再加上一连串以句点分隔的标识符来修饰。标识符必须（MUST）由 ASCII 字母数字和连接号 [0-9A-Za-z-] 组成，且禁止（MUST NOT）留白。当判断版本的优先层级时，版本编译信息可（SHOULD）被忽略。因此当两个版本只有在版本编译信息有差别时，属于相同的优先层级。范例：1.0.0-alpha+001、1.0.0+20130313144700、1.0.0-beta+exp.sha.5114f85。
11. 版本的优先层级指的是不同版本在排序时如何比较。
    1. 判断优先层级时，必须（MUST）把版本依序拆分为主版本号、次版本号、修订号及先行版本号后进行比较（版本编译信息不在这份比较的列表中）。
    2. 由左到右依序比较每个标识符，第一个差异值用来决定优先层级：主版本号、次版本号及修订号以数值比较。

        例如：1.0.0 < 2.0.0 < 2.1.0 < 2.1.1。

    3. 当主版本号、次版本号及修订号都相同时，改以优先层级比较低的先行版本号决定。

        例如：1.0.0-alpha < 1.0.0。

    4. 有相同主版本号、次版本号及修订号的两个先行版本号，其优先层级必须（MUST）透过由左到右的每个被句点分隔的标识符来比较，直到找到一个差异值后决定：

        - 只有数字的标识符以数值高低比较。
        - 有字母或连接号时则逐字以 ASCII 的排序来比较。
        - 数字的标识符比非数字的标识符优先层级低。
        - 若开头的标识符都相同时，栏位比较多的先行版本号优先层级比较高。

        例如：1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0。