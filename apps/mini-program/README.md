# mini-program/ 小程序目录

## 定位

承载基于 AgentForge / taolib 构建的各类小程序，包括微信小程序、支付宝小程序、字节跳动小程序等。

## 技术栈建议

- **微信小程序**：原生框架 / Taro / uni-app
- **支付宝小程序**：原生框架 / uni-app
- **跨平台**：Taro / uni-app / Flutter

## 规范要求

1. **包体积控制**：小程序对包大小有限制，需关注依赖体积。
2. **性能优化**：页面加载速度、渲染性能需符合平台要求。
3. **平台适配**：如使用跨平台框架，需处理平台差异。
4. **API 复用**：优先复用 `taolib` 提供的核心能力，避免重复实现。

## 目录示例

```
mini-program/
├── wechat-agent/            # 微信小程序示例
│   ├── pages/
│   ├── components/
│   ├── app.json
│   └── README.md
└── README.md                # 本文件
```
