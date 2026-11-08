## 改动后的功能验收

工具或接口改动，在 Engine 仓先运行 `node scripts/test-control-plane.mjs`；任一仓内容完成后运行 `harness doctor`。必须覆盖控制面、两仓接口、生成物、依赖、无密钥、Pi/Codex 发现、adapter 契约、投影精确归属和 Profile 引用；退出码就是结论，无法验证的缺口如实说明。

日常保存只检查受影响项，不重复完整 doctor。锁、CAS、快照、回滚与反向复验属于现有保存入口的内置机制，不在这里增加 agent 的手工步骤。
