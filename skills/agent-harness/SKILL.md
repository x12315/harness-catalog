---
name: agent-harness
description: 维护分仓的 Harness Engine 与个人 Catalog。当用户要修改控制面或接口、编排 instruction/skill/Profile、适配新 harness、恢复依赖或排查资源未生效时使用。
license: MIT
metadata:
  repo: "~/.agents"
---

# Harness Engine 与 Catalog 维护

## 先辨归属

1. 用 `harness status --json` 确认 `engine`、`catalog` 和 `interfaceVersion`。工具可以在任意目录，Catalog 默认 `~/.agents`。
2. 改 CLI、Web/TUI、composer、schema、adapter 代码或测试，读 Engine 的 README、`docs/catalog-api.md` 和相邻实现。
3. 改个人指令、Skills、Profiles、依赖、角色/提示词或设置，读 Catalog 的 `../../AGENTS.md`、`../../README.md` 与 `../../profiles/README.md`。

Engine 只依赖 Catalog API v1 数据布局；控制面入口不来自 Catalog 的脚本。Catalog 中 Git hook 仅委托工具。`AGENTS.md`、adapter Profiles 与 Profile schema 副本是生成物，改源码后 `harness compose --apply`。

## 配置与恢复

```bash
harness web
harness profile list
harness compose --apply
harness bootstrap --apply
harness restore
harness reconcile
harness doctor
```

`harness --catalog=<path>` 显式指定数据源；不同 Catalog 有独立锁/CAS，原生 HOME 投影一次只能激活一份。普通 Pi `/harness` 管理清单，`pi-profile <id>` 或 `codex -p <id>` 选择完整工作组合。人工管理不注册模型工具，不受工作 Profile 权限约束。

Instruction 有 mandatory/repository/profile 三层，每条必须有三个完整的 brief/standard/detailed 替代文本。Mandatory 全部启用；Profile 有序选择 `{id,detail}`。Skills 必须显式声明，`[]` 为零，`["*"]` 为全部；推荐模型不覆盖显式会话选择或本机状态。保存按 diff 增量验证，完整 doctor 独立运行，外部写入不覆盖、不自动合并、不抢 stale lock。

共享第三方 Skills 只有官方 skills CLI 可安装，声明进入 `.skill-lock.json`，产物不入库。自有 Skill 的 name 与目录一致，description 写清做什么和何时用，顶层字段规范，新增同步白名单。个人扩展与内置扩展重名时停止，不静默覆盖。

认证、会话、主题、普通默认模型和安装目录在原生路径，任何仓都不收。投影精确指向 Engine 的入口/内置扩展或 Catalog 的数据/个人资源，不能链到上游安装目录。

## 完成标准

工具/接口改动先在 Engine 运行控制面快速测试；两仓内容完成后 `harness doctor`。发布或检查路径改动按 Engine `docs/performance.md` 运行 benchmark、比较基线并归档两仓身份、覆盖和耗时；无法实测或不可比时写明原因。运行中的 Pi 改动需要 `/reload`，旧 Web 服务需重启。

新 harness 实现属于 Engine 的 adapter；Catalog 只提供个人参数。双方契约变更需版本握手与独立目录的失败用例，不能用作者的清单作为工具的必需依赖。
