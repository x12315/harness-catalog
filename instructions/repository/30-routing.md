## 动手前先读哪里

通过 `harness status --json` 确认 Engine 与 Catalog 的位置。工具、接口、adapter 实现及测试变更读 Engine 的 README 和对应源码；个人 instruction、Skill、Profile 及投影/恢复变更读 Catalog 的 README 与 `skills/agent-harness/SKILL.md`。Profile 格式以 Engine 的 `schemas/profile.schema.json` 为准，Catalog 内副本是生成物。

调试、构建或部署超过预计检查点（未估计则 90 秒），或反复轮询没有新证据时，先读 `skills/loop-engineering/SKILL.md`，诊断并缩短反馈回路再决定是否继续等待。
