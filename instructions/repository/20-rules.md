## 投影与生成物

- 投影必须按归属精确指向声明的 Engine 或 Catalog 仓库，禁止链到上游安装目录；上游升级不能静默替换我们的内容。
- 不在生成文件中修补问题；修改其 instruction、Profile 或 composer 来源后重新 compose。
- 人工控制面与工作面分离的既有归属见 `repository/10-ownership`；这里不新增管理能力的验收门槛。
