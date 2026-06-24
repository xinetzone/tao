# 豆包 Seed-2.1 FORCE 大会报道 — 原文提取

> **归档说明**：本文为微信公众号文章原文提取，原位于 `.temp/`，现迁移至 `sources/` 作为长期溯源产物。  
> **来源链接**：https://mp.weixin.qq.com/s/p10dn6zpSR4D5u9BOF9FeQ  
> **作者**：卡兹克、tashi  
> **提取时间**：2026-06-24  
> **提取工具**：defuddle CLI v0.18.1

---

数字生命卡兹克 数字生命卡兹克

在小说阅读器读本章

去阅读

今天，又是每年都非常重磅的火山引擎Force原动力大会了。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqUvThpfHFYxmWx9Y3zkfEn9p3ypYFQFlD9qIKKaibNPVNYBIRicBe8uu9icXibCdx8ic4a13Ip8fIFzhIq1LKbdibuu2NDHow8u5EQEE/640?wx_fmt=jpeg)

有一说一，人是真多啊。

基本上每年这个时候，就是豆包模型全家桶的年度更新。

今年自然也不例外，所有的模型基本就是全面升级。

人在现场，也第一时间给大家总结一下这次大会和我觉得值得说的亮点。

希望对大家有用。

**一. Seed 2.1 Pro**

这个模型，基本就是今天最重头戏了。

今天，正式发布了Doubao-Seed-2.1-pro和Doubao-Seed-2.1-turbo。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqXRGLsmichLyzP6Jys7k6VAM2dEeW7K4FD2o0hUsENYticZIGMnHEBdxmjUHrPoCvLZchrsyty40OUlQDPicHqlgBdBjmA8iaCCaDU/640?wx_fmt=jpeg)

毕竟在这个时代，模型就是一切。

而基础模型，是所有心怀梦想的厂商，永远不可能放弃的话题。

Seed的基模在过去，在2025年初，可以说确实是个很棒的模型，那时候大家都还在卷推理，卷多模态。

可2025年，有太多的事情发生，Manus横空出世，将大家对于Agent的理解向前推了一大步，然后就是Claude Code+Claude让企业客户直接用脚投票，那段时间，Anthropic凭借着Coding和Agent能力的一骑绝尘，甚至将OpenAI都远远甩在了身后。

而Seed慢了，在这个Coding和Agent的能力几乎已经约等于模型智能能力水平的时代里，也逐渐越来越被人遗忘。

而这次基模Seed-2.1-Pro，在憋了很多之后，终于发布了，他们的多模态能力依然是王者，这个你丝毫不用怀疑字节在多模态上的能力，豆包手机和Seedance就能看出来这块的积累，而之前一直以来，都是巨大短板的Coding和Agent能力，在这半年持续不断的猛追之下，在这一次，也终于算是能打了，也终于算是到了可用级别。

老规矩，先看下评分。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqVFMxj2UXGVDzTlyjTWowk5NRbVhgJdnJBBibiaXl4B5Wba34dkF3GGsIGU7iaiaRIC4zR8wAZs8AY3BDVxcBGAJicAGbktcVRbsLQU/640?wx_fmt=jpeg)

Coding能力，确实是补了一大波，有些地方能摸一摸Opus 4.7的级别，比最新一代的模型还是差点了，差距坦诚的讲，还是有的。

Agent能力，也就是各种工具调用还有长程任务上，倒是大幅进化了不少。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVaBX3icoRGCFLX3RYcReqaB0c3acqngQrmIS1k9qYPKqJwFbt1hZrKAZ7ic7Gud9TY4c5ohovnfgSf13Aky1hfgQ9raedjlECc4/640?wx_fmt=png&from=appmsg)

现场还有一个秀Agent能力的我觉得挺牛逼的，还是蛮秀的。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/2jjfQoZLoqU2o5GZ7vzPSIriaksKS5lNhIPA2elJEqQFvQic4Mu4zb8k0LmPJAqg7lMCkbWDwLylkf2O2X5q9zC1YGIgOOl9R0MaZ7jweibxaE/640?wx_fmt=jpeg)

目前Seed-2.1系列在火山、Trae、豆包上等等均已上线，也兼容所有的Agent框架，我直接在Claude Code里测了下。

我对它的评价是，一个非常综合的水桶级模型，虽然在Coding能力上，离Claude这种还有差距，但是这回至少是上桌了，然后他强就强在，水桶。

因为这玩意，在世界知识、多模态上，都有不错的表现。

一个还是多模态的能力，一个基模如果没有多模态，其实我觉得还是比较伤的，就像DeepSeek V4 Pro还有GLM-5.2，Coding能力确实都很强，但是最大的问题，还是没有多模态。

而Seed系列的多模态一直都是国际领先的水平，视觉理解的能力在几乎所有评测集上都是TOP。

你让它看文档、看图表、看视频，基本上能力都非常的强，一个又能写代码又能看图看视频的模型，跟一个只能写代码的模型，在实际业务场景里能做的事情还是有不少差距的。

举个例子，我自己开发的AI资讯监控网站AIHOT上，会对我们所有抓取到的内容进行摘要总结及评分。

比如今天早上抓到的这篇Google的内容，下面那一段文字，就是我对原文的摘要和总结，右上角就是AI系统对它的打分以及是否值得被精选。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqUjSh0BWeGDHbQIU4IRQUER4aeOp3D2lNu06iaRxAAcYh0jZGqgiaUlXerkK7gGDiaicJsnxRHM176JhcOSSDkOIgcia8KLjxOtNjVc/640?wx_fmt=png&from=appmsg)

但这个总结和评分，其实是丢信息的，因为原文里面是有图片的，甚至很多的模型里面，是有视频的。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVkdRMzP2BooOLwNKDsStVgeibPleMZd1RNV93dTo2n0GzEQS5Nh9BlkSPs7c2PCjQMAB959UJpoYZYPVzYQO9AT8rxIk5Zia6qo/640?wx_fmt=png&from=appmsg)

而我背后用的模型，是两个没有多模态能力的纯文本模型，一个小一点的，用来翻译+总结和摘要，一个大一点的，用来评分。

因为丢失了多模态的信息，特别是这个评分，有的时候是不公平的，比如说X上的一些信息，可能只是发了个质量很高的播客视频，但是只简单配了两句话，那就很有可能，是会被我的精选系统过滤掉的。

很多发图片比较多的内容也是如此，比如，小红书和B站，这些上面的一些信息我过去一直没有监控，不是因为我监控的技术手段做不到，是过去我找不到一个比较好的支持多模态的评分模型，所以一直就没干。

那Doubao-Seed-2.1上了之后，我觉得完全可以把背后的这个模型，换成用Doubao-Seed-2.1-turbo来进行摘要，用Seed-2.1-Pro来进行评分，支持我AIHOT上多模态内容的生态。

说干就干，我直接把Claude Code里面的模型，用CC switch换成了Seed-2.1-Pro，让他自己来开发自己。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVMVw6dGzjFRBgCM8jfM9ceYsmicGian8aHdUOf1vsp7JfhN6Lia4zVSu3pLpHGoER67pgTL5NLeugxDkdjzp2rjFeaHtpTP75hw8/640?wx_fmt=png&from=appmsg)

然后把我上面说的那段话，直接当做Prompt，扔了进去，先让他做摘要和总结这块的迭代，因为精选评分那块改模型整体改动太大了，Promtp、阈值、公式算法什么的都需要调整，还要做全量的线上数十万条数据的全量回测，不是一时半会就能干完的。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqWU1rKiauwKIoNDtdxicYFtQ1CpmQGY8ezOIMqDJ3pweH3Up1OhYu3h61xx5ev4a9UkL4gkLibmJeNr1Esg3y4jdxdrkxuZasa0W0/640?wx_fmt=png&from=appmsg)

这个任务开发难度不算很高，但是也没有那么简单，就是我的那个代码，因为后端流程有点复杂了，乱七八糟的细节太多了，而且过去没有把图片扔进去推理的先例，图片缓存和持久化啥的全都没做，所以要考虑的细节还是很多的。

在思考了十几分钟以后，Doubao-Seed-2.1-pro给了我一个详细的方案。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqXtqbIP0D13JwtibFBU8OCafgE1UFOOJX9DWEprZrMibh1icjR45OibDmHiblgpwqm7TcaxmX1dbNHzrNTAqZg7W3rzhibwicNa1ffRaM/640?wx_fmt=png&from=appmsg)

考虑的还是比较全面的，一些对抗性审查的方案还有风险的应对措施，基本都考虑到了。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqV40zn6jqUzJp2A4hUicEF1RRFk26zvzRehHxnTt7wfI24wvibMRLA9WTyGtiayhgc7JUO9IbR8DFwdz6iaxZu4Xuth8qB9ibesmHgA/640?wx_fmt=png&from=appmsg)

没啥问题，我就直接让他开工了。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqUiahD6hMOfIAm4mLWjmAHdQPzmUOHOH1rMg2Xr6NwtPs4BdZDVaLcudbiaoZqia0uVePljVDGZo9DJoJSicEOXl0QTibIFJ7T7UtJ4/640?wx_fmt=png&from=appmsg)

大概在30分钟后，开发完成了。

基本没啥问题，前面的图片缓存、抓取、压缩流程啥的都能跑通，整体都还不错。

但是出现了一个很诡异的BUG，就是莫名其妙的，跑一个文字+多图的摘要，失败了一大半，长的甚至要几分钟之多，我都干懵了，我以为火山的API这么慢？？

结果让它找了半天原因，发现是Doubao-Seed-2.1默认开了深度思考，所以本来就慢，然后自己又给自己写了个300秒超时，然其中一个图片的包装函数又写错了。

改了两轮，搞了10分钟，才把这个事解决，然后让他给我列了一个100条数据的回测报告，这一次，发现推理速度变得极其牛逼，延迟几乎只要3.5s就能直接出。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqW0DksFRbXHXv2LX6DnptjRUSnYuM38IVvOIdO0I94vDcqicP6d8BAUOqDASz71WwrkYTRic9LorywlTHF0VQrv7Ig2V0hTicMUib0/640?wx_fmt=png&from=appmsg)

回测报告的UI展示上，我觉得中规中矩，前端审美是能看的，干净清爽，也没啥特别的错位BUG。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVgR9EJLP4lwRDuMesslvo5dkZH322IBmiaSTEobico8CmTe2VN7Hy1MgpoI1lsZIbeadu3OJ75Xiatx0pvKnbbIxT8Z2uSU7MhY4/640?wx_fmt=png&from=appmsg)

摘要的信息准确性无敌，香爆了。

我感觉我的AIHOT在信息质量上，又要迈向新一波质量的升级了。

然后还有两个点我觉得还是需要说一下，价格和上下文长度。

首先是价格，这个价格相比海外，确实不算贵了，¥6 / ¥30每百万token（输入/输出），但是相比国内DeepSeek这种直接干到个位数级别的爹，感觉还是有优化空间。

上下文还是卡在了256k，没有到达主流的1M，这个还是比较可惜的。

坐等Doubao-Seed的下一个版本了。

**二. 豆包办公模式**

因为Doubao-Seed-2.1-Pro正式发布了，所以，还有一个很重要的功能应该也要即将正式上线了。

也是豆包专业版。

这其中专业版我觉得最核心的功能，我觉得就是我这两天一直在测的，基于Doubao-Seed-2.1-Pro的豆包办公模式，也是豆包的Agent。

因为我已经提前拿到了内测资格，当你打开豆包客户端之后，就能在下面看到这个东西。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVLOINx4opibnE49FgcA8gPYPT1JPEAcUa5zno9RvNzyGMbutqc7QJPCOhAXbIsWzHxJU0ict2my2C8wosibxiboiafaWCG8r0GbDAg/640?wx_fmt=png&from=appmsg)

基于Doubao-Seed-2.1-Pro的办公任务。

Agent时代下驱动的通用办公场景，也是所有厂子我觉得不可能放弃的一环。

豆包的办公模式其实之前就有了，但是之前的体验，坦诚的讲，我自己体验下来，说实话确实一般。

核心原因还是基模，因为之前跑的是Seed 2.0 Pro，这个模型多模态能力很强，理解力也不差，但是在Agent和Coding能力上的短板，导致它在执行一些稍微复杂办公任务的时候，就表现比较一半了。

而这次，底座换成了Seed-2.1-Pro。

不要小看这个"换底座"三个字。对于一个AI产品来说，底座模型的能力升级，可能比产品本身做任何改进都更有效，真的，产品团队搞半年的交互优化、流程重构，在现在，我觉得可能不如底座模型在Agent能力上提升个20%来得实在。

这就是我一直说的，模型就是一切。

我们自己体验下来，变化还是挺明显的。

打开豆包的桌面客户端，在输入框下侧选择办公任务，就能进入。

办公任务下，我们直接选中本地电脑，它就能够去访问到你本地电脑环境中的各种文件。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqXwr1DgCOg5bpVXz9L0WNZJy3SPCNEl47frhh69gU5U4tdDOBosnD7gwfTcgrRsZAZUeuaK2470f6oiaoN0muiaUNe2mgBwiaMLeg/640?wx_fmt=png&from=appmsg)

你可以指定某个项目文件夹，也可以不指定。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqXMr5ZreZwVOgImv6G7n2s159MnkyJ8X4QNCyaiaAcE0zeDmg4Yo9ibI114RzYhYSNjiaXukFhiaTWONiaeiaBYiay2Ba8OVAQtWswUjs/640?wx_fmt=png&from=appmsg)

豆包自己也自带了一堆skills，Agent在执行任务的时候会自动调用。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVnicdfKynxkicRy7ELTas4xxJ4KsRSE3LIVxE9gLwVXnV8Fz7F38qCuY92xRAsXoVMLy99ymFGZicsdOyyibUrKfyugB3Vzwu5LSQ/640?wx_fmt=png&from=appmsg)

我测试了一些任务，在豆包办公模式的表现上，Seed-2.1-Pro整体能力发挥的还不错。

举个例子。

我让它来做我们财务同事之前跟我讲的他们一个工作流。

月底报销的时候，她需要把全公司所有人的发票都汇总到一个飞书多维表格上。

这种活交给Agent来干最合适不过了。

这里出于隐私，我拿1月的发票来演示。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqW7iaf0vpIMznciaYhFZL1uz5lHxREgicbzEiarr5o2ygkZ81Y8VZkxGvpEa6PeGIPoX5ayIjjjsVXwhBEV6VlTLwPOTF9P93QLZ9w/640?wx_fmt=png&from=appmsg)

打开办公模式，我直接在收集了全公司发票的目录下，让他去汇总所有人的发票的信息，按照报销人的格式填到多维表格里面。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqUWzgwQT5kaw0Glj5JzYO3vREZwGtSpDPftjVNHoqTveqzDLOFd1iaGso1SPoljqO1TeISEnC15uDYdxdq3V0RtZ0CmKlS2OyCg/640?wx_fmt=png&from=appmsg)

它会先申请访问文件的权限和执行脚本的权限。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqVMlicSfsggcvyWQPNmibcBy9fticusZHQhmUuqo0U9bHu1jB2v0ASSTkfLKQf8hnn9UicUzbvBHy51iciaKY8Yz83IuicdSDevHBALgo/640?wx_fmt=png&from=appmsg)

然后还会申请飞书文档的编辑权限。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqU2gybuSF7wZMwRiaNzQQAHlUCPESmbr1SoLrL7EptyRL5WOF0VyYSNFopCkmian3E0vlM8S9hYAV2G3ugnVly4qtN9xlzGcrTec/640?wx_fmt=png&from=appmsg)

等你都授权之后，它就库库开始干了。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqUqeV4d8ibKlT8yMCUZTY4utia3LZ0pvJibYCF9DkJJKum6TibORlRzibOD2z0IVoKCUxter6Y2AowHgw0GNUKz3lKcJ4FL5fhd9Apg/640?wx_fmt=png&from=appmsg)

然后就能看到，它把公司各个部门按照每一个报销人，一共210个发票上的信息都提取出来，填到了我指定的多维表格里。

![](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqXNicaaXWv8JlT2nGJfk8F1wiaYADrHicOukqRd8V61Bbicic3jos6aq1qVGZQZpvCSFx93knrNib9yCGFCK0sAudzBia4xvDtkrU2a5k/640?wx_fmt=png&from=appmsg)

基本上没有什么问题，这个就体现出Agent能力和多模态模型的省心省力了。。。

然后测了下联网、收集信息调研的能力。

正好过几个月我们办公室的租期就到了，再加上越来越多的小伙伴加入我们，现在的办公室确实有点坐不下了。

所以我们最近就疯狂的在朝阳找新的、更大的地方。

目前行政那边，根据预算和交通方面的要求，实地也跑了一些，最后选了3个备选方案。

正好昨天下午给我的，我也不太懂，我就把这3个地方丢给豆包，把要求告诉它，让它帮我出一个对比方案，如果有它觉得更合适的地方，也可以推荐。。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVjIPhKsib0YGk6zicSxN63xibTWWQzfMRaROEytYbNarmn7wcodMzRK6u83EfUXaL6PX5jicsUGZfyURnbokXOFHvIUZTgsLRnicdc/640?wx_fmt=png&from=appmsg)

它就去网上搜了一大堆资料，最后给了一份很详细的报告。

先从各个维度全面对比了3个地方，然后分别介绍优缺点，还额外给出了几个推荐的地方。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqUWml1vel13yYWgzadzh0dXxfibPHeqxvUpeJxiatg6ed2lE4koohzCHBmn6he3MKWk4qWqKOHQtrN1owjib0YpZdz1qFZMic1QSkg/640?wx_fmt=png&from=appmsg)

这个租金报价预估，居然基本都是真实的，跟我昨天行政拿给我的报价，几乎就没差个多少钱。。。

同样为了看得更直观，我又让它生成了一个PPT。

它会自动调用做PPT的技能去生成。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqUpAHic4f5dmVT5SW4q6sicaMAeYibolxGia5FjcXRuIsTjQ6zh9oUelbsuDVRmyU9IFt23HIeTK93JP3hAu845lItibCAtoUxp0ezQ/640?wx_fmt=png&from=appmsg)

一轮直出的效果长这样。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqWUgQA3tn7tIrFrATyicpo6IhobPurwmN6SQKSTib30icrQ0owCWTsqAZ1xJfX0LPtibOaGRr3KMaAkX3yJnZZBrNvH4Z9b0vZDp0g/640?wx_fmt=png&from=appmsg)

就只能说，能看，这块我盘了一下，大概率是skill的原因。

这块我建议可以加归藏的PPT skill，可能视觉效果会更好一点。

我自己也拿我之前测一些通用办公任务的30个题目的测试集，在基于Doubao-Seed-2.1-Pro之上的豆包办公任务跑了下回测。

最终效果长这样。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqVDTDxu7IaDmhBNibxiamWqDFNqTLbJmOa8NRPAbibib2Yqic3EhDBrvFrSREhIdksZKuGGIw3CGIVZbMiaT9zsVbNSzt9jMicgf9Ly7Y/640?wx_fmt=jpeg&from=appmsg)

数据分析那边跟Gemini有点像，有时候会自作主张，踩中一些陷阱，比如其中的一道数据分析的题目。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqW7ywWPiaeQnHdLWNNcNbtLbiaWYRuHAxDZmpG1jlick56T8a50K7IdYcZgrK89ZKgFezHtXDYrslibK1tH5HvrVCoOcPERIq6uIs8/640?wx_fmt=jpeg&from=appmsg)

但是整体来说，在有了Seed-2.1-Pro的加持之后，豆包的办公任务，也终于变得还不错了，能在Agent这个通用办公场景上，跟其他家正面开战了。

毕竟，这可是豆包啊。

**三. Seedance**

Seedance这块，作为字节的王者，这次也迎来了一波更新。

Seedance 2.0拥有4K了，而且是原生4K。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqWSZRnIVvYwAhCNJ8jkucMwE9ToIYp9FiaxQMJOTWHoqibbm02MLS9ZhX99Sx7iadyy6GKNxyiancCur8EgdwE47LOqqTdNRT2GWao/640?wx_fmt=png&from=appmsg)

注意，是原生4K，跟后期超分是两回事，现在市面上有不少4K视频，其实就是先生成个720p或者1080p的底子，然后拿超分模型往上拉。

Seedance 2.0模型的质量，配合上4K，基本是可以达到影视级了。

目前已经在火山和即梦上上线。

然后就是新模型，Seedance 2.5。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqW5DhvfEsHXhdiaafwu7ZDWSPnP4lDo1J1hF1Ejr6DaicmyxyuFBoqiaHmAEqBPtYLtjw7xtEmGzo9EsDJ8wkUhP8dOwCBLtWKcgo/640?wx_fmt=jpeg)

更加优秀的运动能力、分镜能力，还有表演质感。

而且，支持30秒的单段原生直出。

直接看视频吧。

而且，现在，还支持在支持在保持画面一致性的同时做局部调整了。

**四. 写在最后**

除了上面三大块之外。

还有两个模型和一些功能我觉得可以快速提一下。

Seedream 5.0 pro，7月初上线。核心升级在于交互式精准编辑，你可以直接在画面上点选、圈选、用箭头标注来表达编辑意图，不需要再用文字去描述空间关系了，还有多图层分离和高密度信息表达能力的提升，一整页PPT的信息量都能准确呈现。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/2jjfQoZLoqXfYoy1vWpZ3Waz26f4bjb4dH3vwtYbntpdwZ3NWnDgBcrFmPMa5zL2qu9XFbfDWMF0ZBa4GYqmZiabsgtPe9ohw66ibgwIx8d3U/640?wx_fmt=jpeg&from=appmsg)

一个全新的音频生成模型。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqWzRMnm0I5NIcBeS37ALFz4D1KTnBmzCibrkfnBqP15aIxIQ5AxfgRYyZjpGrKxZumlf2srSnbia1M1nLuEsB4UkV1YJbU8ZEPTM/640?wx_fmt=jpeg&from=appmsg)

支持用文字、声音参考生成音频、全要素直出（人声+音效+背景音一条Prompt搞定），单次可以生成2分钟音频并且支持延长到几十分钟保持一致性。

对于做有声书和播客的人来说简直是大杀器。

然后，火山方舟CLI也正式发布了，这对我这种后端几乎都在火山上的开发者来说是个大利好。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqVrwgcz6PuSzcNuCq96NooHiaRco1H7xIQDSuyW0J0jR2icKxM4zDl1d2ljVRAxvYn7PrqsyfYJFicNwRylgFD605YyuxZUOKKSzU/640?wx_fmt=jpeg&from=appmsg)

能方便非常多。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqWjPm9Gb8xibCbgdDDCpAYxh2WboVeKMeK5iaMTG4hymQJmmDC8ohW88BWOe2p8BLYiawu8jALh51UHAydwtF5313lgLbqRVBwgics/640?wx_fmt=jpeg&from=appmsg)

整体大概就是这样。

![](https://mmbiz.qpic.cn/mmbiz_jpg/2jjfQoZLoqXUEmCvROxmG5Yd90vDhjZOvZvVeV0jTQcVTIIrLe0cicBrZicYNCjsugcjLib77MbGTVdoDy5TEicrRjSDvIHgX1VjQ87ePfQIFlY/640?wx_fmt=jpeg&from=appmsg)

说到底还是那句话，模型就是一切。

字节，也在向Coding和Agent，全面进军了。

******以上，既然看到这里了，如果觉得不错，随手点个赞、在看、转发三连吧，如果想第一时间收到推送，也可以给我个星标⭐～谢谢你看我的文章，我们，下次再见。******

\>/ 作者：卡兹克、tashi

\>/ 投稿或爆料，请联系邮箱：wzglyay@virxact.com
