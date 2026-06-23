# File Structure

- Modify: `.agents/scripts/check_env.py`
  - 责任：校验本地工具链可用性、版本基线、配置一致性；从 `mise.toml` 读取工具层版本。
- Modify: `README.md`
  - 责任：面向人类开发者说明当前推荐的环境初始化入口。
- Modify: `AGENTS.md`
  - 责任：面向 AI 助手说明当前唯一推荐的环境入口与禁止路径。
- Optional Modify: `docs/quickstart.md`
  - 责任：若发现仍存在历史入口描述，则统一为 `mise run init` / `mise run init-check`。
- No create: 本轮不新增代码模块，避免扩大范围。
