## 投影与生成物

1. 核对投影实际解析的来源与归属，必须精确指向声明的 Engine 代码或 Catalog 数据源，不能链向上游安装目录；上游升级不得静默替换仓库内容。
2. `AGENTS.md`、adapter Profiles 等生成物不手改。发现问题时修改 instruction、Profile 或 composer 源码，再由 compose 重新生成。
3. 人工控制面与工作面分离的既有归属见 `repository/10-ownership`。只读 Profile 不阻断人工维护是该归属的说明，不在本条另加验收门槛。
