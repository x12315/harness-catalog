# 指令开关与迁移

本页供维护 Catalog 的用户查找全局开关、选择详略和迁移拆分后的旧选择。这里只说明指令，不改变 Profile 的模型、工具或 Skills 选择。

## 层级和详略

- `instructions/selection.json` 的 mandatory/repository 选择生成全局 `AGENTS.md`。Mandatory 安全词条不能关闭；repository 可独立启停，不随 Profile 切换。
- `profiles/*.json` 的 `instructions` 只选择 profile 层词条，不能关闭全局规则。Skills 是另一份选择，不等于 repository 策略开关。
- 每个 ID 都有 `<id>.brief.md`、`<id>.md`、`<id>.detailed.md` 三个完整替代文本，分别是 brief、standard、detailed。详略改变篇幅，不改变行为强度；关闭用启停选择，不用 brief 代替关闭。对齐档位不能把原详细档独有的额外门槛提升为默认要求；细节可以保留为解释和例子，不能成为新的必做步骤。
- 使用 `harness web` 或 `/harness instructions` 管理全局词条，审阅变更后由 `harness compose --apply` 生成。不要手改 AGENTS 或 adapter 生成物。磁盘更新后当前会话仍需 `/reload` 或重选 Profile；保存不证明会话已生效。

## 全局 repository 开关

以下 ID 均以 `repository/` 为前缀。保留旧 ID 的主职责，其余职责移到相邻的新 ID，而不是为每句话建立开关。

| 旧 ID | 保留的职责 | 新 ID 及职责 |
| --- | --- | --- |
| `00-purpose` | 仓库定位（未改） | 无 |
| `10-ownership` | 分层归属（未改） | 无 |
| `20-rules` | 投影精确归属、生成物从来源生成、人工控制面分离 | `21-own-skill-tracking` Git 白名单；`22-skill-metadata` 元数据与命名；`23-model-precedence` 模型推荐与本机选择 |
| `25-engineering-judgment` | 基于风险和证据的判断（未改） | 无 |
| `30-routing` | Catalog/Engine 阅读入口 | `31-feedback-checkpoints` 超时/无新证据时加载当前可用的反馈 Skill 并诊断 |
| `35-long-task-goals` | 长任务持久记录的创建、更新、重读与记录位置交接 | `36-goal-scope-continuity` 总体目标、范围与完成判断；`37-blocker-handling` 按依赖暂停和继续 |
| `40-validation` | 功能验收和日常增量检查 | `41-performance-validation` 发布/检查执行路径的性能验收 |
| `50-conventions` | 沟通语言与准确说明结果 | `51-preparation` 读取与工具探测；`52-code-style` 风格、最小实现与提交约定；`53-profile-transition` 切换后的资源与能力重判；`54-runtime-refresh` 内容更新后的验收反馈和生效提醒 |

开关并非对其他规则的否定。例如关闭投影词条，不会取消仍启用的分层归属规则；关闭阻塞词条，不会取消 mandatory 的权限边界或风险判断中的依赖处理。用户和项目的独立要求同样仍有效。

## 长任务记录与反馈 Skill

`35-long-task-goals` 只要求长任务持久记录：开始时创建或复用，中途识别长任务立即补记，在里程碑等节点更新，恢复、换任务和完成前重读。按项目约定优先复用任务文档、issue 或跟踪系统，没有约定时建最小文件；没有强制的 `TASK.md` 或其他固定文件名。记录目标、范围、验收、授权限制、进度证据、未完成、阻塞与下一步，不将秘密或会话入库；决策背景可按实际需要补充，不另设必填字段。

- **35 关闭，loop-engineering 开启，且无其他明确记录要求：** 可以设置假设、可观察信号、90 秒等检查点和总预算，在当前交互中诊断与报告，不自动创建持久任务文件。
- **35 开启：** 长任务按所选档位的同一契约创建/复用、更新和重读记录；非长任务不为该策略另建文件。
- **35 关闭，但用户要求任务文档/交接，或项目明确要求记录：** 按该独立要求执行。关闭可选策略不是禁止用户请求。
- **31 关闭：** `30-routing` 不再强制因等待加载反馈 Skill。Skill 仍可能因当前任务匹配或用户明确请求而加载，但不能借加载重新启用 35 或其他已关闭策略；不可用的 Skill 不自动恢复。

## 功能、性能验收与生效提醒

Catalog 自有 `agent-harness` Skill 和 README 不另设验收政策，只引用当前启用的 `repository/40-validation`、`repository/41-performance-validation`、`repository/54-runtime-refresh` 或用户/项目明确要求。

- **41 关、40 开：** 适用的功能验收仍在，但维护 Skill、README 和 54 不自动要求 benchmark。
- **40 关：** 维护 Skill、README 和 54 不另要求全量测试或 doctor；41 是否适用独立判断。
- **54 开、40/41 关：** 只保留生效提醒，不恢复关闭的验收要求，也不自动刷新会话。
- **全部关闭但用户/项目明确要求某项验收：** 遵循该独立要求；关闭可选策略不是禁止明确请求。
- **任何组合：** CLI 自带的校验、锁/CAS、快照、verify、apply/install/reload 检查保持原样。指令关闭不是绕过程序检查的授权。mandatory 权限、秘密保护与真实报告同样不变。

命令示例和运行时流程是显式执行时的参考，不是加载维护 Skill 后的自动执行清单。样本数、预算和基线方法在适用时参考 Engine 性能文档；本次拆分不额外增加固定样本数、人工审批或重建基线门槛。

Catalog 自有 `loop-engineering` 遵循记录开关边界。第三方 `session-handoff` 内容未修改；若另行明确触发它或其他文档要求，应单独判断其适用要求，不能承诺仅关闭 35 会撤销所有外部记录要求。

## 本次来源复核边界

本次来源交付清单共 **54 个文件**：48 个 instruction Markdown（三档各 16 项）、1 个 selection JSON、2 个自有 Skill、3 个文档。追加的自有维护 Skill 为 `skills/agent-harness/SKILL.md`。撤回先前为统一三档而提升的额外门槛：固定性能样本/预算/人工重建基线、手工复制保存保护步骤、每项改动必读生成链、按逻辑拆分提交、记录额外决策/失败字段、委派与固定收尾流程等；相关内容改为解释或交给明确的独立要求，不新增默认步骤。35 仍启用；原有选择与档位保留，新条目继承对应父项的启用状态和档位。Profile JSON、模型、工具和 Skills 选择未改。

源码变更由 `harness compose --apply` 生成，不手改生成物；保存、生成物校验与当前会话加载分别确认。已经运行的会话须重新加载，旧历史中的指令或 Skill 文本不代表当前选择。

## 迁移旧选择

本次来源选择中，原有 9 项都已选择：mandatory safety 为 standard，purpose 与 routing 为 brief，其余 repository 为 standard。没有关闭任何旧项；新增项紧随其父项并继承父项档位。具体为：

- `21`、`22`、`23` 继承 `20` 的 standard；`31` 继承 `30` 的 brief。
- `36`、`37` 继承 `35` 的 standard；`41` 继承 `40` 的 standard。
- `51`、`52`、`53`、`54` 继承 `50` 的 standard。
- mandatory、`00`、`10`、`25` 的选择和内容不变；现有 Profile JSON 不变。

这是本 Catalog 的一次来源迁移，不是 Engine 的通用自动迁移功能。今后手动将相同拆分应用到别的选择时：

1. 以迁移前的来源选择为准，不以已有文件或生成物标题推断是否启用。
2. 原 ID 已选择时保留它，在其位置后按上表顺序插入新 ID，继承该次选择的 detail；选中即启用、从选择列表移除即关闭，不添加 schema 未定义的 enabled 字段。保持其他项顺序和设置。
3. 原 ID 未选择时，保留其源码文件不等于默认启用，新子项也保持未选择；不要因为 ID 仍存在就全部开启。
4. 若某些子项已有独立配置，审阅并保留明确选择，不重复插入或覆盖。三档都必须存在，不能用 standard 回填用户的 brief/detailed。
5. 审阅覆盖和选择后 compose，分别确认生成结果与当前会话加载状态；不要以源码保存当作运行时生效。
