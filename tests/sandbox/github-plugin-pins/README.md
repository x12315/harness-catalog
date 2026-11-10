# GitHub plugin pins：只安装与解析

Catalog 自有 consumer case，`target=macos-tart`、`display=cli`。不改 Profile/设置/基底，不启动 Pi 会话、扩展工厂、模型、TUI、浏览器或宿主查看器。Tart 默认 NAT，GitHub 公共仓需联网；这不是无网隔离测试。

## 输入与运行（先审阅，再由操作者执行）

将已审阅的**冻结受管 SDK 完整运行时**归档放到：

```text
.artifacts/github-plugin-pins/pi-sdk-runtime.tar.gz
```

此文件必须被主 agent 加入忽略规则并确认不被 Git 跟踪。不要把 SDK、node_modules 或归档提交到 Catalog。`push` 只传该文件与三份测试源码；runner 会把归档字节包含在 `project-source.sha256` 快照中。

归档根必须是 `node_modules/`（不是外层 content-ID 目录），包含全部受管 SDK 依赖及相对内部 symlink，不能引用宿主绝对路径。主 agent 应从已核对的 frozen runtime 制作归档，并核对其 content ID/来源及快照 SHA，不能以相同 npm 版本号替代。guest 将其解包到本次 job 的 `runtime/`，直接绝对导入：

```text
runtime/node_modules/@earendil-works/pi-coding-agent/dist/core/package-manager.js
runtime/node_modules/@earendil-works/pi-coding-agent/dist/core/settings-manager.js
```

不依赖 guest 全局 Pi，不现场安装或重建 SDK。guest 需已有 Node >=22.19、npm、Git、Python3、tar；缺项直接失败，不修改基底。macOS/ARM64 SDK 归档只能用于匹配平台。SDK API、布局或资源不匹配直接失败，不使用替身。

主 agent 在授权的一次性 guest 路径运行：

```sh
EXECUTION=local /path/to/agent-harness-sandbox/bin/test.sh \
  --project /Users/montana/.agents github-plugin-pins
```

已验用例 `20261110T043916Z-20953` 的 guest/runner/assert 均为0/PASS；第一次运行因 npm 拒绝两个配置层共用同一空文件而失败，记录保留。修正为两个独立空配置后重新运行通过。使用的是受管 `aa46e64c41add5ed05dd52b90a3851f686d6bb1a2ad335c4d697b189c70446bb` 配套 SDK，不把相同版本号当相同API；上游原版SDK若缺少所需方法应明确失败。测试本身不执行宿主SDK或插件工厂。

## 验收契约

- guest 先验证 Darwin 和 `kern.hv_vmm_present=1`，拒绝裸机执行；VMM 检测不替代 runner 的一次性克隆/销毁保证。
- `install-only.mjs install` 调用真实 `DefaultPackageManager.install`，不用 `installAndPersist`。npm 使用 `--ignore-scripts --no-audit --no-fund`；两个固定 manifest 没有运行时/开发依赖或安装生命周期脚本，仅有 host peers。
- 两个模式都用 `SettingsManager.inMemory({packages: pins, ...}, {projectTrusted:false})`，显式 `agentDir`、`cwd`。从该 candidate 的 `getPackages()` 获取来源，调用 `resolveExtensionSources(..., {installMissing:false})`，只解析候选包，避免扫描宿主个人资源；不使用会执行工厂的 resource loader。
- helper 导入 SDK 前丢弃继承的 Pi/Profile/overlay/认证环境，只保留 PATH、指定 scratch HOME/TMPDIR；公共 Git/npm 不读个人或系统 Git config、npm user/global config。`PI_OFFLINE=1` 仅禁自动网络，不替代 installed-only 契约，也不禁止显式 Git 安装。没有权限绕过参数。
- guest 给 native/agent/project settings 和 overlay 写入无效 JSON 哨兵；inMemory 不读它们。安装与解析后字节快照不变。不会读取、复制或创建凭据/会话。
- `pins.json` 固定两条完整来源 SHA、原 Profile 包名、入口路径及逐文件 SHA。检查真实 Git HEAD、`git ls-files -z -- extensions package.json` 的完整集合和每个文件字节。
- 集合哈希公式：路径字典序排列，逐项更新 SHA256 为 `UTF8(path) + NUL + rawBytes + NUL`。Window 为 4 文件 `cd5280a0…`，Fast 为 2 文件 `146fd5e5…`。预期值只读计算自与给定 HEAD 相符的本地公开源码；不 vendor 内容。
- npm 可能生成 `package-lock.json`：明确从资源哈希排除，报告其存在与 `git status --porcelain`；不声称整个 checkout pristine。tracked `extensions/` 与 `package.json` 另验无差异。
- install 后独立再跑 resolve；HEAD、资源哈希、状态及解析结果必须相同，无 settings/progress errors。日志输出 API 调用、Git 检查命令、真实安装路径、HEAD、资源哈希、SDK 两个模块的 SHA，不输出环境值或秘密。
- 宿主 `assert.sh` 只读取 rc、快照清单和 JSON 数据，严格匹配 `github-plugin-pins/sdk-result` 两条及 `github-plugin-pins/guest-result` 一条；不导入 SDK，不安装、不执行插件，不要求 GUI 截图。

通过仅证明固定包的 SDK 安装/installed-only 解析与字节一致；不证明扩展可执行、reload、窗口创建、Fast 请求行为或当前会话已生效。此 case 不改变任何静态 Profile，故没有要求刷新现有会话。

## 可复用 helper（审阅与额外授权后才可用）

同一个 helper 可在明确授权的宿主 cache 安装中复用；测试用例本身不会执行宿主安装。`SDK_ROOT` 是含 `node_modules/` 的冻结 runtime 根，`PLUGIN_AGENT_DIR` 是经授权的 cache 所属原生 agent 目录。必须已有显式目录，并提供独立的新 scratch HOME/cwd；不要传当前 Profile 临时 agentDir。

```sh
# 仅为后续授权操作的配方；scratch 及其 home/cwd 由调用者提前创建。
env -i PATH="$PATH" HOME="$scratch/home" \
  SDK_ROOT="$reviewed_frozen_runtime" \
  PLUGIN_AGENT_DIR="$authorized_native_agent_dir" \
  PLUGIN_CWD="$scratch/cwd" \
  node /Users/montana/.agents/tests/sandbox/github-plugin-pins/install-only.mjs install
# 同样环境，末尾用 resolve：不安装、不 fetch、不更新。
```

`install` 可能对同仓已存在 cache 做 fetch/reset/clean，应先审阅该目标并保留需要的本地改动；这不是覆盖未知工作树的授权。helper 不保存设置，也不改启用引用。`resolve` 缺 cache、ref 不符或缺 SDK API 时失败，不自动降级到安装。
