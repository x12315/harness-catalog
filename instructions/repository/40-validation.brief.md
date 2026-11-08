## 改动后的功能验收

工具/接口改动先在 Engine 跑 `node scripts/test-control-plane.mjs`；任一仓内容完成后 `harness doctor`，覆盖控制面、两仓接口、生成物、依赖、无密钥、Pi/Codex 发现、adapter、精确投影和 Profile 引用，退出码定结论，缺口如实说明。日常保存只检查受影响项，不重复完整 doctor；保存入口自带的检查与保护不受此开关影响。
