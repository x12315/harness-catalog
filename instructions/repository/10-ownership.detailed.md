## 分层归属

| 归属 | 内容 | 写入方 |
| --- | --- | --- |
| Engine 仓 | CLI、Web/TUI、composer、adapter 代码、schema、工具版本和测试 | 工具开发 |
| Catalog 仓 | instructions、Profiles、自有 Skills、第三方 lock、预期差异、个人 adapter 设置/角色/提示词 | 用户管理 |
| Catalog 生成物 | AGENTS.md、adapter Profiles、Profile schema 副本 | composer |
| 原生运行目录 | npm/git 安装、adapter 私有资源、认证、会话、个性化 | 官方工具；声明过的 adapter |
| 原生投影 | CLI/扩展入口指向 Engine；指令/Profile/个人资源指向 Catalog | bootstrap |

Catalog 中的 Git hook 仅调用已安装的 `harness`，不复制实现。工具不从 Catalog 加载控制面代码；自有 Skill 内容及明确声明的个人扩展仍是 Catalog 资源。

一个 harness 一个 adapter，厂商配置只能出现在 adapter 或 Profile 的 `adapters.<name>`。中立 instruction 和自有 skill 不携带厂商配置。生成物禁止手改，改来源后 compose。共享第三方 Skills 只有 `skills` CLI 可以安装；自有 Skills 由 Git 管理。固定版本 adapter 可生成原生私有资源，不能写入共享 Skills，verify 必须精确验证它们。第三方内容不入库，安装为整目录替换。

`harness` / `/harness` 是人工控制面，不受工作 Profile 的工具 allowlist 限制，也不注册为模型工具。厂商私有 Profile 编辑器不得改写 adapter 生成物。
