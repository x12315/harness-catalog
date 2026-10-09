## 改动后的硬验收

工具或接口改动，在 Engine 仓先运行 `node scripts/test-control-plane.mjs`；任一仓内容完成后运行 `harness doctor`。必须覆盖控制面、两仓接口、生成物、依赖、无密钥、Pi/Codex 发现、adapter 契约、投影精确归属和 Profile 引用；退出码就是结论。

发布版本或检查执行路径改动，按 Engine 的 `docs/performance.md` 运行 `harness benchmark` 并与历史报告比较，归档两仓身份、覆盖和耗时。不可比或无法实测时写明原因，不能把夹具耗时当作真实性能。日常保存只检查受影响项，不重复完整 doctor。
