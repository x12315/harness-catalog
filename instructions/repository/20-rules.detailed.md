## 仓库硬规则

1. 投影必须精确解析到声明的 Engine 代码或 Catalog 数据源，不能链向上游安装目录；上游升级不得静默替换仓库内容。
2. `skills/` 默认整体忽略，只对白名单中的自有 skill 放行；新增自有 skill 同步更新 `.gitignore`。
3. `SKILL.md` 只使用规范顶层字段：`name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools`；厂商字段进入 `metadata:`。
4. Skill 的 `name` 与目录同名；`description` 同时说明能力与触发条件，保证路由可靠。
5. `AGENTS.md` 和 adapter profile 是生成物。发现问题时修改 instruction、Profile 或 composer 源码，再重新生成。
6. Profile 推荐的 provider、model 与 thinking 是工程声明；认证、主题、最后选择和 UI 状态仍是本机个性化。
7. 命令行、会话或用户显式模型选择优先于 Profile 推荐，不把正常覆盖误报为漂移。
8. 新增管理能力时保持控制面与工作面分离，避免只读 Profile 阻断人工维护。
