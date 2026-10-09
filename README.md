# Personal Harness Catalog

个人使用的公开 Harness 清单，独立于 [Harness Engine](https://github.com/x12315/agent-harness)。公开的是工程声明与自有内容，不是认证、会话、机器个性化或第三方安装产物。

## 归属

- `instructions/`：mandatory / repository / Profile 词条的三档正文及常驻选择。
- `profiles/`：工作方案、模型推荐、指令/Skills 选择和 adapter 参数。初始 `heavy`、`medium`、`ultralight` 只是可编辑预设，不是固定数量。
- `skills/`：自有内容白名单入库；第三方由官方 skills CLI 根据 `.skill-lock.json` 安装，目录默认忽略。
- `adapters/`：个人 Pi 设置、角色、提示词，Codex 附加说明和生成 Profiles。工具扩展实现属于 Engine，不在这里维护。
- `harness.catalog.json`：Catalog API v1 握手；`expected-gaps.json` 声明允许的依赖差异。
- `AGENTS.md`、adapter Profiles、`profiles/profile.schema.json`：生成物，改来源后 compose，不手改。
- `scripts/git-hooks/pre-commit`：只委托已安装的 `harness` 作本仓验收，不复制工具实现。

## 本机使用

默认路径 `~/.agents`。工具可克隆到任意位置；本机目前是 `~/agent-harness`。通过 `harness status --json` 查看双方实际位置与接口版本，不从 Catalog 猜工具路径。

```bash
harness web                         # 常规配置入口：新建、复制、改显示名称、删除
harness profile list
harness compose --apply
harness bootstrap --apply
harness restore                     # 默认仅打印官方安装命令
harness doctor
pi-profile heavy
pi-profile medium
pi-profile ultralight
codex -p medium
```

未安装入口时从 Engine 运行 `node scripts/harness.mjs --catalog=/path/to/catalog compose --apply`，再 bootstrap。不同位置用 `--catalog=<path>` 或 `HARNESS_CATALOG`。旧单仓的 `node scripts/...` 不再是本仓维护入口。

普通 Pi 的 `/harness` 是人工管理面；`pi-profile` 在启动边界选择完整工作组合。普通用户默认模型、主题、scope、临时选择仍是本机个性化，显式选择优先于 Profile 推荐。

Web/TUI 修改按实际 diff 增量检查，完整 doctor 独立运行。CAS/锁冲突时刷新后审阅，不手工抢锁；正常失败恢复来源与生成物。删除需准确输入 ID，至少保留一个方案，不删共享资源、认证或会话。改配置后正在运行的 agent 需要 `/reload` 或重新选择 Profile；旧 Web 服务须关闭后重新 `harness web`。

## 公共仓安全

认证使用环境变量、钥匙串或 harness 原生存储。`.env`、auth.json、私钥、会话和安装目录永不入库。提交前和发布前检查源码/暂存区；工具仓与本仓有独立 Git 历史和验收身份。第三方内容不 vendor；依赖升级由官方工具完成后对账。

自有 Skill 新增必须更新 `.gitignore` 白名单；name 与目录一致，description 写清能力和触发条件。instruction 三档是完整替代，mandatory 全部启用，Profile 词条有序引用。

工具、schema 或接口问题在 Engine 修复；本仓只改个人声明。格式和协议见 Engine 的 `docs/catalog-api.md` 与 `schemas/profile.schema.json`；性能验收见 `docs/performance.md`，每次发布保留真实多轮报告、两仓身份与覆盖。用例夹具耗时不代表真实安装态性能。

## 历史与恢复

本公共仓使用独立新历史，只发布审阅后的当前清单；原混合历史保留在私有 Engine 仓及快照，避免把私有工具源码通过历史公开。未删除认证或改动原历史。当前树已移除工具实现。拆分前快照和投影清单保存在本机临时目录，发布证据另归档；这些不是 Git 内容。

生成物漂移用 `harness compose --apply`，投影漂移用 `harness bootstrap --apply`。实体冲突先快照并交给人处理；脚本不覆盖实体。恢复依赖用 `harness restore --apply`，再 reconcile/doctor。无法取得凭据或审批时停止并交给人，不自行提权。
