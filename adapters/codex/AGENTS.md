# Codex personal entry

修改 Harness 时，先运行 `harness status --json` 确认 Engine 与 Catalog 位置，再读对应仓 README。工具实现和 schema 属于 Engine；个人指令、Profiles、Skills 和配置属于 Catalog。

Catalog 的 mandatory/repository 规则由 composer 直接注入每个 Codex Profile 的 developer_instructions，不依赖此文件的标题或 home 路径指针。认证、会话与安装产物保持在原生目录；显式会话设置优先于工程推荐。
