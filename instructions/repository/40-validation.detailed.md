## 改动后的功能验收

1. 修改工具控制面、composer、schema、adapter 或两仓接口，先在 Engine 运行 `node scripts/test-control-plane.mjs` 获取快速反馈。
2. 任一仓内容完成后运行 `harness doctor`，验证接口版本、控制面 RPC、生成物无漂移、依赖与磁盘一致、无密钥、Pi/Codex 发现、adapter 契约、精确投影来源及 Profile 引用；退出码决定通过或失败，未验证项明确列出。
3. 日常保存只检查受影响项，不在每次保存时重复完整 doctor。Web/TUI 现有入口按 diff 增量检查，并内置锁、CAS、快照、回滚和反向复验；这是入口行为说明，不是另加一套 agent 手工验收步骤。
