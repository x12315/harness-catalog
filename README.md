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

以下命令和运行时说明是操作参考，不是读取 README 后自动执行的清单。Agent 的可选工作流要求只来自当前实际启用的 instruction 或用户/项目明确要求：功能验收见 `repository/40-validation`，性能验收见 `repository/41-performance-validation`，生效提醒见 `repository/54-runtime-refresh`。关闭某项不会由本页或自有 `agent-harness` Skill 重新启用；54 也不恢复关闭的 40/41。CLI 自带的校验、锁/CAS、快照和 verify 等执行契约不受指令开关影响，mandatory 权限、秘密保护与真实性边界始终有效。

默认路径 `~/.agents`。工具可克隆到任意位置；本机目前是 `~/agent-harness`。通过 `harness status --json` 查看双方实际位置与接口版本，不从 Catalog 猜工具路径。

```bash
harness web                         # 常规配置入口：新建、复制、改显示名称、删除
harness profile list
harness compose --apply
harness bootstrap --apply
harness restore                     # 默认仅打印官方安装命令
harness doctor
pi-h                                # 受管配套 Pi/Profile，默认方案由本机偏好选择
harness run pi heavy                # 显式命名方案，仍使用受管运行时
harness run pi medium
harness run pi ultralight
codex -p medium
```

未安装入口时从 Engine 运行 `node scripts/harness.mjs --catalog=/path/to/catalog compose --apply`，再 bootstrap。不同位置用 `--catalog=<path>` 或 `HARNESS_CATALOG`。旧单仓的 `node scripts/...` 不再是本仓维护入口。

本地迁移保留了 `loop-engineering`；`iterm-bell` 的提醒实现已迁入 Engine，并消费 Observer 的会话状态，Catalog 只保留启用声明。当前四个 Profile 均明确启用它们、`pi-session-window` 和 `@calesennett/pi-codex-fast`（Profile 使用完整包名，包括 scope，不是扩展文件名）。Fast 速度模式继续保留在原生个性化设置，Profile 继承；DeepSeek 不支持 priority。Pi 的已保存模型范围也会继承，范围内不含推荐模型时可能选其他模型；需要特定模型时显式传 `--model`，不要为了修复扩展改动本机范围。独立插件由 `adapters/pi/settings.json` 固定GitHub提交：会话窗口为 `git:github.com/x12315/pi-session-window@8fef6d472a90d6217603fc42def22d795a3f3967`，Fast为 `git:github.com/calesennett/pi-codex-fast@b2538cbdb4e78efe4388878e6a11599d4f10cf02`；不再依赖Desktop开发树。Git安装缓存仍在本机，必须由Pi包管理器准备，不手抄源码到vendor；已有Desktop源码保留，不自动重载。`pi-web-ui` 保持已知可用的 `npm:pi-web-ui@0.100.0`，不将未核验构建产物的Git树冒充同等安装包。Engine内置扩展继续精确投影到Engine源码，不改成第三方Git包。

Pi 的 `/harness` 是人工管理面；`pi-h` / `harness run pi <id>` 使用本机选择的配套包。直接 PATH `pi`、`pi-profile` 保持原安装，不保证使用同一包。普通用户默认模型、主题、scope、临时选择仍是本机个性化，显式选择优先于 Profile 推荐。

Web/TUI 修改按实际 diff 增量检查，保存不自动切换当前会话。配套 Pi/Profile 支持保存后 `/reload`：在锁/CAS/快照下静态生成、投影、检查，重解析所有受管计划（包括内置 default）并刷新一次，不逐次完整 doctor。默认工具基线按离开普通模式前的实际有效选择更新，保留手动禁用项。需要完整部署验收时可用 `/harness apply`；该入口先 compose/bootstrap/完整 verify 再刷新，是否额外执行验收服从当前启用的 `repository/40-validation` 或用户/项目要求。CLI `harness apply` 只部署磁盘并完整 verify，`harness refresh` 仅磁盘静态准备，不安装、联网、请求模型或注入已有会话。

本机配套不可变包已完成标准构建、安装及真实 `pi-h` 原生 TUI/reload 验收；能力以 content ID、完整包验证及会话 `/harness status`、`/harness help` 为准，不以相同版本号判断。旧进程不能靠 reload 获得新 Pi/Profile，须从外部终端通过 `pi-h` 正常重启一次。每个会话按 [Engine 热激活流程](../agent-harness/docs/hot-activation.md) 单独确认。reload 仅用本地安装/缓存，缺失或不匹配在 shutdown 前以隔离候选设置检查失败，重试不污染 live 状态；运行时发现不查询 npm wrapper。预检不执行扩展代码，不保证所有扩展可加载或 shutdown 后事务回滚。

运行时维护见 [Engine 本地分发流程](../agent-harness/docs/local-distribution.md)（Engine 不在相邻目录时先用 status 定位）：`harness runtime build/install/status/verify/rollback` 在用户原生目录管理配套包，不替换普通 PATH Pi/Profile。安装离线、禁 lifecycle scripts、复用锁定工件，先验证再以锁/CAS 更新选择；已选择但损坏时停止，不自动回退 PATH。源码更新不会自动改变不可变包，修改 Pi/Profile 须新 build/install；Engine/Catalog 投影仍精确指向各自仓库，不 vendor 或手改安装目录。Engine 扩展编辑后 reload，CLI 下次命令生效，Web 服务重启。

CAS/锁冲突时刷新后审阅，不手工抢锁；正常失败恢复来源与生成物。删除需准确输入 ID，至少保留一个方案，不删共享资源、认证或会话。旧 Web 服务须关闭后重新 `harness web`。

Web 的“安装与管理”可填写本地路径、远端 Git/npm 来源、固定版本和期望位置，生成待核验的 AI 管理任务；页面和复制动作不执行安装，也不授权 agent 实施。先让 agent 展示实际命令、落盘位置、安装/启动代码风险、所有引用与恢复方案，再明确批准。取消引用不等于卸载，卸载受管副本不删除个人源码、认证、会话或本机偏好。官方工具不支持指定位置时须暂停；权限或凭据交给人处理，不绕过。

独立发布的个人扩展和第三方包日常优先使用固定 Git commit/tag 或 npm 版本；本地路径是明确的开发引用，不是发布渠道。切换前必须确认远端包含当前修复，不自动提交或推送。Catalog 内自有 Skills/资源本身由 Catalog Git 管理，按源码归属投影，不复制到安装缓存后再反向引用。

## 后台任务完成通知

`skills/background-task-notify/SKILL.md` 是独立的自有 Skill，负责无需 agent 持续盯守的后台任务交接、结果校验与完成/失败通知；“完成后告诉我”“下载完通知我”由它触发。当前四个 Profile 都显式启用它，不依赖 `loop-engineering`。后者只负责工程反馈回路、实验检查点和调试预算。

实际执行与系统通知由 Engine 的 `harness task` 提供，Skill 不另写监控服务。使用前确认通知权限；不承诺主动发送聊天消息或跨关机自动恢复。首次本机通知配置需用户允许，运行中的 agent 用 `/reload` 或重新选择 Profile 加载新 Skill，不自动刷新会话。

## 浏览器协作与独立后台

`skills/browser-work-mode/SKILL.md` 是项目无关的自有配套规范，与第三方 `agent-browser` 一起使用；当前启用浏览器的 `medium`、`ultralight`、`feiyu` 同时声明两者，未给 `heavy` 新增浏览器能力。明确要共同查看/接手则选可见协作，独立查询、抓取、测试默认后台；能合理推断就自行选择，有实质歧义才简短询问。用户明确选择优先，已有模式只沿用同一任务，不变成永久偏好。

原生CLI从 [个人fork固定提交](https://github.com/x12315/agent-browser/tree/887bb8bc4f44e85f292b7d27c845fb56fe19751a) 和 [固定GitHub Release](https://github.com/x12315/agent-browser/releases/tag/x12315-work-mode-0.39.1-r1) 引入，资产校验及并行安装见该提交的 `docs/work-mode-distribution.md`；不是把Rust仓库伪装成Pi插件。实际安装目录是本机缓存，不替代GitHub来源身份。

两种模式隔离会话与页面控制。新任务发现并行入口 `agent-browser-work-mode` 时优先选择它，并通过同一入口读取配套core、执行后续操作；已有任务仍使用先前确认的原CLI，不因安装新版自动迁移。普通 `agent-browser` 与既有会话不被替换。当前CLI与配套core明确提供原生 `--work-mode` 时优先调用工具的sticky会话与冲突保护；旧CLI只在新建独立会话时兼容 `--headed true/false`，不冒称具备原生保护，也不自动安装fork或迁移活跃daemon。Skill只处理意图与协作规则，不再实现一套会话工具，不改第三方安装Skill。协作需确认用户实际能看见并操作，交接后重新读取页面；后台不占协作窗口，不静默附着个人浏览器、不迁移认证或重启有未保存/未知提交的会话。浏览器headless不等于任务可脱离agent长期运行，跨轮通知另走已有后台设施。细节与校准情形见该Skill及其 `evals.md`；内容规则不构成工具硬强制或真实浏览器行为验收。运行中的agent需 `/reload` 或重新选择Profile加载，不自动刷新。

## 本地产物链接

`skills/artifact-view/SKILL.md` 是 Catalog 自有的交付规范；四个当前 Profile（`heavy`、`medium`、`ultralight`、`feiyu`）均声明该 Skill 和 Pi `file-links` 扩展。扩展及原生 Markdown renderer 的适配实现属于 Engine。使用简短标签和完整真实绝对路径交付文件；renderer 将本地路径转换为编码后的 file URL，经原生 OSC 8 交给系统默认应用。仅在需要展示排版时生成 HTML，默认不打开宿主机窗口、不改变默认应用、不创建软链接。

兼容性取决于当前会话实际加载的扩展和 Pi Markdown renderer，Profile 声明、新进程或虚拟机验收均不能代替当前会话的链接交付确认。适用的功能验收要求来自当前启用的 `repository/40-validation` 或用户/项目要求，完整部署入口为 `/harness apply`；配套运行时中日常 `/reload` 静态准备后重解析并刷新普通/命名计划，具体能力见 `/harness status`。激活前旧进程须通过 `pi-h` 重启一次，不能仅靠 reload 更新 Pi/Profile。扩展尚未加载时，使用用户已确认有效的可见短路径回退，不输出依赖新扩展的蓝色链接；软链接只在明确需要时使用。主动打开测试仅在现有 `~/Desktop/agent-harness-sandbox` 虚拟机内进行，无宿主机测试回退。

## 公共仓安全

认证使用环境变量、钥匙串或 harness 原生存储。`.env`、auth.json、私钥、会话和安装目录永不入库。提交前和发布前检查源码/暂存区；工具仓与本仓有独立 Git 历史和验收身份。第三方内容不 vendor；依赖升级由官方工具完成后对账。

自有 Skill 新增必须更新 `.gitignore` 白名单；name 与目录一致，description 写清能力和触发条件。instruction 三档是同一行为的完整替代，只改变详略，不改变强度。`instructions/selection.json` 管理全局 AGENTS 的 mandatory/repository 词条；mandatory 不可关闭，repository 可独立启停，不随 Profile 切换。Profile 只管理其有序的 profile 词条引用。

长任务持久记录由当前启用的 `repository/35-long-task-goals` 独立控制；关闭它不会禁止用户明确要求或项目独立规定的任务文档/交接。第三方 `session-handoff` 未修改，只有另行明确触发时才单独判断其适用要求；本页不保证关闭 35 会撤销所有外部文档要求。`loop-engineering` 只按当前有效要求维护记录，不因加载 Skill 自动创建任务文件。总体目标连续性、阻塞处理、反馈检查点、功能与性能验收等各有独立开关；当前拆分保留原有启用状态、档位和相对顺序，见 [指令开关与迁移](docs/instruction-controls.md)。

`skills/ponytail/` 为本 Catalog 原创同名实现，替代原第三方安装声明，保留三个 Profile 的调用名称。它负责发现最短可行执行路径：优先复用并补齐现有路径，必要时才增添路径。代码、命令、流程、人工操作与控制通道都属于这个判断范围，不能因没有写代码就认为没有新增复杂性；也不以复用为由拒绝确实需要的新能力。不再受编码专用触发或代码优先输出约束。独立的 `repository/25-engineering-judgment` 常驻词条负责具体风险、证据缺口与最小可验证保障，不依赖 ponytail 被触发，也不放宽 mandatory 权限边界。内容级检查与模拟决策用例不能当作真实运行的安全证明，校准情形见 `skills/ponytail/evals.md`。

工具、schema 或接口问题在 Engine 修复；本仓只改个人声明。格式和协议见 Engine 的 `docs/catalog-api.md` 与 `schemas/profile.schema.json`；性能验收是否适用见当前启用的 `repository/41-performance-validation` 或用户/项目要求；适用时的方法参考 Engine `docs/performance.md`。本页不另设多轮测量或固定样本门槛，也不因读取维护 Skill 自动运行 benchmark。用例夹具耗时不代表真实安装态性能。

## 历史与恢复

本公共仓使用独立新历史，只发布审阅后的当前清单；原混合历史保留在 Engine 仓及本机快照。Engine 也已公开，公开前复查了完整历史的凭据风险；两仓独立历史用于分离工具与个人清单的演进。未删除认证或重写原历史。当前树已移除工具实现。拆分前快照和投影清单保存在本机临时目录，发布证据另归档；这些不是 Git 内容。

生成物漂移用 `harness compose --apply`，投影漂移用 `harness bootstrap --apply`。实体冲突先快照并交给人处理；脚本不覆盖实体。恢复依赖用 `harness restore --apply`，再 reconcile/doctor。无法取得凭据或审批时停止并交给人，不自行提权。

## 许可证

本仓库的自有指令、配置、文档和 Skills 采用 [MIT License](LICENSE)。Pi 派生角色与提示词保留上游版权与许可，见 [第三方说明](THIRD_PARTY_NOTICES.md)。声明的第三方依赖仍遵循各自许可；本许可不包含任何账号、认证或服务使用权。
