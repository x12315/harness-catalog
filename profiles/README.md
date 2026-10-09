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

三个档位是同一行为契约的替代文本，不做增量拼接。修改或新增 entry 时必须同时维护三档。

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

## Profile 字段

- `label` / `description`：人类可读名称与用途。
- `instructions`：有序的 `{ id, detail }` 选择；只允许引用 `instructions/profile/`。
- `skills`：必须显式声明。`[]` 表示零 Skills，`["*"]` 表示全部，其余为名称或 glob 白名单。
- `adapters.pi`：Pi tools、extensions、MCP 与推荐 provider/model/thinking。每个 Profile 必须保留 `harness-manager`。
- `adapters.codex`：Codex 原生 model、reasoning、sandbox 与 approval。

模型推荐是工程声明。认证、主题、最后选择和命令行/会话覆盖仍是本机状态；显式选择优先。

## 人类管理路径

普通 `pi` 是管理入口，`/harness` 是人类触发的原生 extension command，不向模型注册 tool：

- `/harness web` / `harness web`：打开 [Catalog 配置入口](../README.md#本机使用)，新建、复制与删除方案、横向比较、搜索/批量调整、预览实际词条并审阅保存；与 TUI 使用同一 Catalog。
- `/harness instructions`：管理 AGENTS.md 常驻词条。Repository 可逐项启停；mandatory 锁定。每项都可选详略、预览和编辑源码。
- `/harness skills`：搜索 Skill 摘要并查看完整说明；不修改 Profile。
- `/harness configure <name>`：管理某个 Profile 的 instruction entries、Skills 与推荐模型。Skill 开关使用有界摘要；Pi 模型从当前 session scope（或已认证 provider）选择，Codex 可跟随 Pi，只有无法枚举的 Codex 模型才需要高级手动输入。
- 每层菜单都提供“返回上级”；原始 JSON 编辑仅作为高级排错入口。
- Web/TUI 保存按变更范围增量检查：名称/说明只检查配置与投影，adapter 字段只检查当前方案对应运行时，共享词条只检查受影响方案；新建/删除才更新投影。完整 `doctor` 独立运行，不阻塞日常保存。正常失败会恢复源码并按反向变更范围复验。Web/TUI 共用 Catalog 锁；如果来源并发变化则拒绝覆盖，保留快照等待人工审阅。

完整 Profile 的资源由 Pi 在启动时发现，因此工作会话在启动边界选择：

```bash
pi                              # 普通 Pi；使用 /harness 管理 Catalog
pi-profile heavy                # DeepSeek 走量代码
pi-profile medium               # Terra 日常调试与知识工作
pi-profile ultralight           # Astra 复杂设计与全局规划
codex -p medium                 # Codex 原生 Profile
```

由 `pi-profile` 启动的会话可用 `/profile use <name>` 热切换。`harness run pi|codex <name>` 仅保留为脚本化/恢复别名；Pi 仍拥有进程、TUI 与 extension 生命周期，Harness 只提供资源、组合声明和启动时适配。

Pi tools 是严格 allowlist。Subagent 派生进程的工具还会与父 Profile 当前活动工具取交集，并排除递归 `subagent`，不能借角色声明恢复父级未开放的能力。

## 上游边界

- `pi-profile-switch@0.11.0` 负责 Pi 的解析、隔离 runtime、热切换与 overlay；仓库不 fork 它。
- 该版本生成私有 `profile-config` skill 并强制带入 Profile runtime。普通 Pi 通过精确排除隐藏它；runtime 的 opt-out 等待 [VincentFF/pi-profile-switch#64](https://github.com/VincentFF/pi-profile-switch/issues/64)。
- 省略 `skills` 会收窄为零，省略 `extensions` 也不会保留普通用户扩展，因此 schema 强制显式声明。
- Codex 当前要求 `skills.config.path` 指向具体 `SKILL.md`，composer 使用当前 Catalog 的具体 `skills/<name>/SKILL.md` 路径。

Profile 名不能是 `default`，它是 `pi-profile-switch` 的内置全量模式。
