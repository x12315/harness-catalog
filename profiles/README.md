# Harness Profiles

`profiles/*.json` 是跨 harness 的组合声明。它们选择 instruction entries、skills 和 adapter 原生资源；不复制资源，也不安装第三方内容。

## Instruction entries

Instruction catalog 分三层：

- `instructions/mandatory/`：不可关闭的安全边界。
- `instructions/repository/`：生成到全局 `AGENTS.md` 的仓库规则，可在控制面逐项启停。
- `instructions/profile/`：由每个 Profile 选择，编译为 Pi `instructions` 与 Codex `developer_instructions`。

每个 entry 有三个完整、可独立使用的 Markdown 版本：

| 档位 | 文件 | 用途 |
| --- | --- | --- |
| 精简 | `<id>.brief.md` | 只保留改变行为所需的核心约束 |
| 标准 | `<id>.md` | 日常默认，兼顾约束与上下文负担 |
| 详细 | `<id>.detailed.md` | 展开步骤、边界、例外和完成条件 |

`instructions/selection.json` 选择 mandatory 与 repository 的启用状态和详略。Mandatory 必须全部出现，只能换档，不能关闭。Profile 使用有序对象数组选择词条：

```json
"instructions": [
  { "id": "profile/implementation", "detail": "standard" },
  { "id": "profile/concise", "detail": "brief" }
]
```

三个档位是同一行为契约的完整替代文本，只改变详略，不改变强度，也不做增量拼接。三档同步维护的来源约定见 `skills/agent-harness/SKILL.md`；详细档可展开解释和例子，不应为对齐档位把额外门槛提升为默认要求。

全局 repository 选择不会因切换 Profile 而关闭；Profile 的 `instructions` 只能引用 profile 层，不能覆盖全局开关。长任务持久记录单独由 `repository/35-long-task-goals` 控制；关闭它不禁止用户明确要求或项目独立规定的任务文档、交接。`loop-engineering` 被启用或加载不等于重新启用该记录策略；没有其他明确要求时可直接使用反馈回路方法而不创建任务文件。总体目标连续性、阻塞处理、反馈检查点与功能/性能验收分别管理。自有 `agent-harness` Skill 同样不独立启用可选验收：功能、性能与生效提醒分别服从当前启用的 `repository/40-validation`、`repository/41-performance-validation`、`repository/54-runtime-refresh` 或用户/项目明确要求；本页的命令是参考，不会自动要求全量测试、doctor 或 benchmark。CLI 内置的检查和 mandatory 安全/真实性边界不随这些开关关闭。第三方 `session-handoff` 未修改；另行明确触发时单独判断其要求，关闭 35 不撤销外部的明确文档要求。完整开关、三档语义和旧选择迁移见 [指令开关与迁移](../docs/instruction-controls.md)。

## 三个初始预设

预设是初始配置，不是固定的方案数量或不可删除的系统项。通过 `harness web` 的“配置方案”页可以新建、复制、修改名称或删除方案，至少保留一个。名称与启动 ID 分离；改名称不改变命令，换 ID 请复制后删除原方案。操作和安全边界见 [Catalog 使用方式](../README.md#本机使用)。

名称表示**脚手架重量**，不是模型价格或问题难度：

| Profile | 推荐模型 | 主要用途 | 默认脚手架 |
| --- | --- | --- | --- |
| `heavy` | Pi `deepseek/deepseek-flash` | 走量代码生成 | 详细 implementation + 弱模型约束 + 编码 Skills |
| `medium` | `gpt-5.6-terra` | 调试、中量编码、建议问答、知识索引 | 标准 instruction + 编码、文档和知识空间 Skills |
| `ultralight` | `gpt-6-astra` | 空间设计、疑难排查、复杂问题、全局规划 | 最少过程约束 + strategic entry + 设计与探索 Skills |

Codex 不提供 DeepSeek，因此 `heavy` 的 Codex adapter 推荐 `gpt-5.6-luna`，这是手工选择同名 Profile 时的替代配置，不是自动故障转移。

三个预设都是可写工作环境。临时只读要求应通过词条、工具声明或独立会话明确配置，不能仅依赖文件 sandbox 约束远端 API。

## 肥鱼方案

`feiyu`（肥鱼harness）面向 DeepSeek Flash 的日常编码、排障、设计和飞书工作。沿用中型的三条标准指令（implementation、model-standard、concise），要求多步任务先作简短计划、核实关键假设、执行相关验证，不采用重型的详细逐步约束。

技能使用显式白名单：包含超轻当前全部 40 项技能，以及中型独有的 `amap-house-hunting`、`git-commit`、`make-repo-contribution`，合计 43 项。保留超轻的 `subagent` 工具与扩展，其他工具权限不扩大；没有新增依赖或修改已有方案。

Pi 推荐 `deepseek/deepseek-flash`，思考档位 `high`。该 ID 是服务端别名，本机模型目录当前标注为 **DeepSeek V4.1 Flash**，不是固定到 V4.0 的版本；支持 low/high/max，不使用不支持的 medium。模型推荐不覆盖本机已保存的默认模型或显式会话选择，必须使用 Flash 时从外部终端启动：

```bash
harness run pi feiyu --model deepseek/deepseek-flash --thinking high
```

已有受管 Pi 会话可用 `/harness switch feiyu` 切换；切换后确认实际模型，必要时在 `/model` 选择 Flash。新建方案不会自动切换当前会话或修改默认启动方案。

Codex 不支持 DeepSeek；`codex -p feiyu` 使用与中型相同的 `gpt-5.6-terra` / `medium` 作为独立替代配置，不是 Pi 失败时的自动切换。配置和运行时验收不代表已验证模型在真实任务中的效果。

## Profile 字段

- `label` / `description`：人类可读名称与用途。
- `instructions`：有序的 `{ id, detail }` 选择；只允许引用 `instructions/profile/`。
- `skills`：必须显式声明。`[]` 表示零 Skills，`["*"]` 表示全部，其余为名称或 glob 白名单。
- `adapters.pi`：Pi tools、extensions、MCP 与推荐 provider/model/thinking。每个 Profile 必须保留 `harness-manager`。
- `adapters.codex`：Codex 原生 model、reasoning、sandbox 与 approval。

模型推荐是工程声明。认证、主题、最后选择和命令行/会话覆盖仍是本机状态；显式选择优先。

## 后台任务完成通知

当前四个 Profile 均在 `skills` 中显式声明独立的 `background-task-notify`，用于后台任务交接、业务结果校验与完成/失败通知。保留 `loop-engineering` 的原有声明，但通知能力不通过它间接启用；两者没有 Skill 依赖，工具、扩展和模型配置不因此改变。

该 Skill 复用 Engine `harness task`；首次系统通知权限由用户配置。声明保存后 compose 生成 Pi/Codex 引用，运行中的 agent 仍需 `/reload` 或重新选择 Profile，不自动切换或刷新会话。

## 本地产物链接

当前四个 Profile（`heavy`、`medium`、`ultralight`、`feiyu`）均在 `skills` 中启用 Catalog 自有 `artifact-view`，在 `adapters.pi.extensions` 中启用 Engine 所有的 `file-links`。它们使用简短 Markdown 标签和真实绝对路径；原生 renderer 负责编码 file URL 与 OSC 8，保留系统默认应用。HTML 仅用于需要排版的展示，默认不打开宿主机窗口或创建软链接；软链接只是旧 renderer 的可选兼容回退。

这些声明须经 Engine 生成、投影后才可供运行时加载。配套 Pi/Profile 支持保存后 `/reload`：静态准备后重解析所有受管计划（包括内置 default）并刷新一次，不逐次完整 doctor；默认工具基线按离开普通模式前的实际有效选择更新，保留手动禁用项。本机配套不可变包已安装并通过真实 `pi-h` 原生 TUI/reload 验收，但激活前旧进程须先通过 `pi-h` 重启一次，不能靠 reload 获得新 Pi/Profile。通过 `/harness status`、`/harness help` 查看会话能力，再以 `/profile status` 核对实际资源。声明、新进程检查或虚拟机验收均不代表当前会话已经能够点击交付；扩展尚未加载时，使用已确认有效的可见短路径回退。主动打开测试仅在现有 `~/Desktop/agent-harness-sandbox` 虚拟机内完成，不回退到宿主机。

## 人类管理路径

`pi-h` 是受管会话入口，`/harness` 是人类触发的原生 extension command，不向模型注册 tool；普通 `pi` 保持原安装：

- `/harness web` / `harness web`：打开 [Catalog 配置入口](../README.md#本机使用)，新建、复制与删除方案、横向比较、搜索/批量调整、预览实际词条并审阅保存；与 TUI 使用同一 Catalog。
- `/harness instructions`：管理 AGENTS.md 常驻词条。Repository 可逐项启停；mandatory 锁定。每项都可选详略、预览和编辑源码。
- `/harness skills`：搜索 Skill 摘要并查看完整说明；不修改 Profile。
- `/harness configure <name>`：管理某个 Profile 的 instruction entries、Skills 与推荐模型。Skill 开关使用有界摘要；Pi 模型从当前 session scope（或已认证 provider）选择，Codex 可跟随 Pi，只有无法枚举的 Codex 模型才需要高级手动输入。
- 每层菜单都提供“返回上级”；原始 JSON 编辑仅作为高级排错入口。
- Web/TUI 保存按变更范围增量检查：名称/说明只检查配置与投影，adapter 字段只检查当前方案对应运行时，共享词条只检查受影响方案；新建/删除才更新投影。完整 `doctor` 独立运行，不阻塞日常保存。正常失败会恢复源码并按反向变更范围复验。Web/TUI 共用 Catalog 锁；如果来源并发变化则拒绝覆盖，保留快照等待人工审阅。

完整 Profile 的资源由 Pi 在启动时发现，可在启动边界选择：

```bash
pi-h                            # 受管运行时；本机默认方案，未设置时普通模式
harness run pi heavy            # DeepSeek 走量代码
harness run pi medium           # Terra 日常调试与知识工作
harness run pi ultralight       # Astra 复杂设计与全局规划
codex -p medium                 # Codex 原生 Profile
```

受管 Pi 会话可用 `/harness switch <name>` 或 `/profile use <name>` 切换组合。当前启用的 `repository/40-validation` 或用户/项目要求需要完整部署验收时，可用 `/harness apply`：完整磁盘 gate 成功后，支持新 API 时通过公开 `ctx.requestReload()` 进入高层准备；该环境的原生 `/reload` 也走高层入口，Harness 由 `registerReloadHandler()` 接入。既有 Profile 切换、reload、overlay 命令的 `ctx.reload()` 保持低层提交，不重复解析或丢失待提交配置。CLI `harness refresh` 仅磁盘静态准备，不安装、联网、请求模型或注入会话；CLI apply 另做完整 verify。

配套包由 `harness runtime` 显式管理，流程见 [本地分发](../../agent-harness/docs/local-distribution.md)；Engine 不在相邻目录时先用 `harness status --json` 定位。相同版本号不代表同一包或能力，以来源 hash、归档 SHA、content ID、完整验证及会话状态为准。修改 Pi/Profile 须新 build/install 并启动新进程，源码保存不会更新不可变包；Engine 扩展仍从仓库投影，修改后 reload，CLI 下次命令生效，Web 服务重启。直接 PATH `pi-profile` 不保证使用受管包；`harness run pi <id>` 明确使用所选包。已选择但损坏时停止，不静默回退全局安装。

reload 仅用本地安装/缓存，缺失或不匹配包在 shutdown 前通过隔离候选设置检查失败，重试不污染 live 状态；运行时发现不查询 npm wrapper。包预检不执行扩展代码，不保证所有扩展加载成功或 shutdown 后事务回滚。磁盘回执与当前页脚、`/profile status` 分别确认，详见 [热激活流程](../../agent-harness/docs/hot-activation.md)。Web 保存不等于切换当前会话。

配套 Profile 会话可用 `/profile use <name>` 热切换。`harness run pi <name>` 是显式选择受管命名方案的入口，`harness run codex <name>` 保留为 Codex 脚本化别名；Pi 仍拥有进程、TUI 与 extension 生命周期，Harness 只提供资源、组合声明和启动时适配。

Pi tools 是严格 allowlist。Subagent 派生进程的工具还会与父 Profile 当前活动工具取交集，并排除递归 `subagent`，不能借角色声明恢复父级未开放的能力。

## 上游边界

- 配套 `pi-profile-switch` 包负责 Pi 的解析、隔离 runtime、热切换与 overlay；Catalog 不承载其实现。受管构建来自已审阅的独立 Pi/Profile 工作树，不将源码或第三方包复制进 Catalog。
- Profile 当前生成私有 `profile-config` skill 并强制带入 Profile runtime。普通 Pi 通过精确排除隐藏它；runtime 的 opt-out 等待 [VincentFF/pi-profile-switch#64](https://github.com/VincentFF/pi-profile-switch/issues/64)。
- 省略 `skills` 会收窄为零，省略 `extensions` 也不会保留普通用户扩展，因此 schema 强制显式声明。
- Codex 当前要求 `skills.config.path` 指向具体 `SKILL.md`，composer 使用当前 Catalog 的具体 `skills/<name>/SKILL.md` 路径。

Profile 名不能是 `default`，它是 `pi-profile-switch` 的内置全量模式。
