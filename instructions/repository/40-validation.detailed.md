## 改动后的硬验收

1. 修改 Engine 控制面、composer、schema 或两仓接口，先在工具仓运行 `node scripts/test-control-plane.mjs` 获取快速反馈。
2. 两仓内容改动完成后运行 `harness doctor`，同时验证接口版本、控制面 RPC、生成物无漂移、依赖与磁盘一致、无密钥、Pi/Codex 发现、adapter 契约、精确投影源和 Profile 引用；退出码决定通过或失败。
3. 发布版本或调整检查执行路径时，读取 Engine 的 `docs/performance.md`，运行真实 `harness benchmark`，保留每种模式至少 3 个样本、检查覆盖、两仓源码身份和宿主版本；与同环境历史报告比较并按显式预算验收。
4. 环境、工作量或覆盖变了，报告不可比，人工审阅后重建基线。无法实测时明确缺口；不缓存通过结果，不拿隔离夹具的耗时替代真实 runtime，不用删除检查制造提速。
5. Web/TUI 日常保存按真实 diff 增量检查，并保留锁、CAS、快照、回滚与反向复验；完整 doctor 和多轮性能测量是独立入口。
