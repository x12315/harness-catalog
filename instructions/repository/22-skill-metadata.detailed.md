## Skill 元数据契约

1. `SKILL.md` frontmatter 顶层只使用 `name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools`；厂商专有字段进入 `metadata:`，不能另加顶层字段。
2. `name` 与 Skill 所在目录同名。
3. `description` 同时说明能力与触发条件，保证路由可靠；不能只写用途而省略何时使用。
