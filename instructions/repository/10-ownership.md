## 分层归属

- **Engine 仓**：CLI、Web/TUI、composer、adapter 实现、schema、依赖工具固定版本与测试。
- **Catalog 仓**：`instructions/`、`profiles/`、自有 `skills/`、`.skill-lock.json`、`expected-gaps.json`、个人 adapter 配置与生成物。`scripts/git-hooks/pre-commit` 仅委托已安装的工具，不承载实现。
- **本机原生目录**：安装产物、认证、会话和个性化，不入库。投影按归属精确指向 Engine 或 Catalog，不能链到上游安装目录。

一个 harness 一个 adapter。厂商字段进入 adapter 或 Profile 的 `adapters.<name>`；中立 instruction 与自有 skill 不承载厂商配置。

`instructions/`、`profiles/` 是源码；`AGENTS.md`、生成的 adapter Profiles 与 Profile schema 副本由 `harness compose --apply` 生成。共享第三方 Skills 仅由固定版本的 `skills` CLI 安装，自有 Skills 由 Git 管理；adapter 私有资源只写原生目录并由 verify 精确检查。第三方内容不 vendor，安装按整目录替换。

人工管理通过 `harness` / `/harness`，不受工作 Profile 工具权限约束；不使用厂商私有编辑器修改生成物。
