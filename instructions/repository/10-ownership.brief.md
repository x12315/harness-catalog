## 分层归属

Engine 拥有代码、schema 和测试；Catalog 拥有指令、Profiles、Skills、依赖清单、个人 adapter 配置及生成物。认证与运行状态不入库。投影按归属指向两仓，第三方共享 Skills 仅由 `skills` CLI 安装。源码修改后 compose，生成物不手改；人工管理不受 Profile 工具权限约束。
