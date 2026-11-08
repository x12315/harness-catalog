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

`harness --catalog=<path>` 显式指定数据源；不同 Catalog 有独立锁/CAS，原生 HOME 投影一次只能激活一份。Pi `/harness` 管理清单，`pi-h` 启动本机选择的配套包，`harness run pi <id>` 或 `codex -p <id>` 选择完整工作组合。直接 PATH `pi` / `pi-profile` 保持原安装，不保证使用受管包。人工管理不注册模型工具，不受工作 Profile 权限约束。

Instruction 有 mandatory/repository/profile 三层，每条必须有三个完整的 brief/standard/detailed 替代文本。Mandatory 全部启用；Profile 有序选择 `{id,detail}`。Skills 必须显式声明，`[]` 为零，`["*"]` 为全部；推荐模型不覆盖显式会话选择或本机状态。保存按 diff 增量验证，完整 doctor 独立运行，外部写入不覆盖、不自动合并、不抢 stale lock。

共享第三方 Skills 只有官方 skills CLI 可安装，声明进入 `.skill-lock.json`，产物不入库。自有 Skill 的 name 与目录一致，description 写清做什么和何时用，顶层字段规范，新增同步白名单。个人扩展与内置扩展重名时停止，不静默覆盖。

认证、会话、主题、普通默认模型和安装目录在原生路径，任何仓都不收。投影精确指向 Engine 的入口/内置扩展或 Catalog 的数据/个人资源，不能链到上游安装目录。

## 验收策略与操作参考

本 Skill 不独立启用可选的 agent 工作流验收要求。功能验收遵循当前实际启用的 `repository/40-validation`，性能验收遵循 `repository/41-performance-validation`，生效提醒遵循 `repository/54-runtime-refresh`，或用户/项目明确的独立要求。关闭某项后，不因加载本 Skill 或阅读命令示例重新要求该项；尤其不会自动运行 benchmark。40 开、41 关时只保留适用的功能验收；40 关时本 Skill 不另要求全量测试或 doctor；54 不重新启用关闭的 40/41。

适用时的命令参考：Engine 控制面快速测试为 `node scripts/test-control-plane.mjs`，完整检查为 `harness doctor`；性能测量为 `harness benchmark`，方法见 Engine `docs/performance.md`。这些是可执行配方，不是加载本 Skill 后必须执行的清单。权限、秘密保护和真实报告仍受 mandatory 安全边界约束；未运行或无法验证就如实说明。

上述开关只控制 agent 额外执行哪些工作，不关闭或绕过 CLI 自带的校验、锁/CAS、快照、verify 或 apply/install/reload 内置检查。以下描述命令能力与显式执行时的契约，不要求自动激活、安装、测试或刷新。

激活流程见 Engine `docs/hot-activation.md`（先用 status 定位 Engine）：配套 Pi/Profile 运行时支持保存后 `/reload`：通过 `registerReloadHandler()` / `ctx.requestReload()` 在锁/CAS/快照下静态生成、投影、检查，再重解析所有受管计划（包括内置 default）并低层刷新一次，不逐次完整 doctor。普通完整设置与工具刷新需要两者匹配；默认工具基线按离开普通模式前的实际有效选择更新，保留手动禁用项。既有 Profile 切换/reload/overlay 的 `ctx.reload()` 保持低层提交，不重复准备。需要完整部署验收时可用 `/harness apply`；该入口在完整 compose/bootstrap/verify 成功后才请求高层刷新。CLI `harness refresh` 仅磁盘静态准备，不安装、联网、请求模型或注入会话；CLI apply 另保留完整 verify。

运行时维护先读 Engine `docs/local-distribution.md`。`harness runtime build --pi-source=<path> --profile-source=<path> --out=<new-directory> --json` 复用官方 Node 离线模型数据打包路径；`harness runtime install --manifest=<path> [--expected-hash=<hash|none>] --json` 使用锁定工件，在私有 staging 离线禁 lifecycle scripts 安装，验证后才以锁/CAS 更新原生选择。`harness runtime status --json` 查看 content ID、previous 与 selectionHash；`harness runtime verify --json` 校验完整归档/安装树及 SDK/Profile 能力；`harness runtime rollback [--expected-hash=<hash|none>] --json` 显式回退，previous 为 null 时恢复未受管 PATH。占位符用当前 status 值替换，不复用旧 CAS hash。没有受管选择可兼容 PATH；已选择但损坏时失败，不自动回退。

判断运行时能力时不要仅凭版本号：核对完整来源文件集合 hash、包 SHA、content ID 和回执，并用 `/harness status`、`/harness help` 核对实际会话。旧进程不能靠 `/reload` 或更新 manager 获得新 Pi/Profile，须从外部终端通过 `pi-h` 正常重启一次；配套进程之后才日常 reload。源码更新不自动改变不可变包，修改 Pi/Profile 须新 build/install 并启动新进程；Engine 扩展编辑后 reload，Engine CLI 下次命令生效，Web 服务重启。Engine/Catalog 投影继续精确指向各自仓库，不 vendor、不手改安装目录或把固定依赖改指未发布源码。

新 reload 对缺失/不匹配 npm、Git 或本地包在 shutdown 前以隔离候选设置检查失败，重试不污染 live 状态；运行时发现只用本地安装/缓存，不查询 npm wrapper、不安装或下载。最终加载同样 installed-only，但预检不执行扩展代码，不保证所有扩展可加载或 shutdown 后事务回滚。核验激活结果时，磁盘回执、页脚和 `/profile status` 分别提供不同证据；失败保留日志与必要恢复信息，不以磁盘成功覆盖 Pi 加载错误。持久记录是否必须维护仍服从当前启用的 `repository/35-long-task-goals` 或用户/项目明确要求。安装包能力、上游完整源码测试、付费模型、GUI 和性能是不同结论，不互相代替。

新 harness 实现属于 Engine 的 adapter；Catalog 只提供个人参数。双方契约的版本握手属于接口约束，不能用作者的清单作为工具的必需依赖；独立目录的失败用例是接口验收的参考方法，是否要求执行遵循当前启用的 `repository/40-validation` 或用户/项目明确要求，不因加载本 Skill 自动运行测试。
