## 仓库定位

Harness Engine 与个人 Harness Catalog 是两个独立 Git 仓。Engine 拥有 CLI、Web/TUI、composer、adapter 代码、schema 与验证；Catalog 拥有 instructions、Profiles、自有 Skills、第三方 Skills lock、个人 adapter 配置和编译生成物。

通过 `harness status --json` 获取两边位置。Catalog API v1 使用固定数据布局和 `harness.catalog.json` 的 `schemaVersion: 1`；`harness --catalog=<path>` 或 `HARNESS_CATALOG` 显式选择，默认 `~/.agents`。工具不执行 Catalog 的控制面脚本，不依赖作者的方案数量、模型或指令内容。第三方安装、认证、会话、个性化与运行状态由官方工具管理，均不入库。
