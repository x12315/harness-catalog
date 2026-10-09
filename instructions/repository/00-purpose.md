## 仓库定位

Harness 工具与个人 Catalog 分仓：工具仓拥有控制面、composer、adapter 实现与验收；Catalog 仓拥有 instruction、skill、Profile 和个人 adapter 配置。接口为 Catalog API v1，位置由 `harness --catalog=<path>` 或 `HARNESS_CATALOG` 选择；默认 `~/.agents`。第三方安装、认证与机器运行状态仍由官方工具负责。
