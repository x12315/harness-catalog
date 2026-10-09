## 动手前先读哪里

1. `harness status --json` 返回 Engine/Catalog 路径、接口版本和资源状态；先确认要修改哪一仓。
2. CLI、Web/TUI、composer、schema、adapter 与测试改动，读 Engine README、`docs/catalog-api.md` 和相邻源码。
3. 个人 instructions、Skills、Profiles、依赖声明、adapter 设置，读 Catalog README、`profiles/README.md` 与 `skills/agent-harness/SKILL.md`。
4. 投影、恢复、依赖或本机事实问题，先查看两仓归属和官方运行目录，不把安装或认证状态移入仓库。
5. schema 的真相源在 Engine，Catalog 内副本由 compose 更新。旧单仓的 `node scripts/...` 不是 Catalog 的维护入口，使用 `harness`。
