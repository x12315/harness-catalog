---
name: background-task-notify
description: 将无需 agent 持续盯守的已授权工作交给后台，保存结果并在完成或失败后通知用户。当用户要求“完成后告诉我”“下载完通知我”，或 agent 需要结束当前轮次而工作仍应独立运行时使用。
license: MIT
metadata:
  ownership: catalog-original
---

# 后台任务完成通知

把可独立运行的工作交给现有 `harness task` 工具；agent 可以结束本轮或继续其他工作，由后台 worker 校验结果并发送系统通知。不为每个任务另写 PID 轮询和通知脚本。

## 适用边界

- 任务已经获授权，参数、目标和完成条件明确，不再需要 agent 持续决策或交互。尚需用户登录、验证码、审批或现场判断时，先处理真正受影响的步骤，不把它伪装成可无人值守的任务。
- 复用已有命令、校验程序和明确的完成回执；已有工作正在运行时，先确认状态和副作用，不为获得通知而重复执行。已有作业可用其明确的完成回执接入，不能仅凭某个 PID 消失推断成功。
- 凭据不放进标题、命令参数、日志或任务定义；使用工具原生凭据存储或环境变量。

## 1. 确认入口与通知权限

先探测 `command -v harness`，用 `harness status --json` 定位 Engine，阅读其 `docs/background-tasks.md`，再执行：

```sh
harness task notify status
```

只有 `authorization: authorized` 且 `alerts: enabled` 才能承诺交给系统通知；`start` 也会内置检查。不在通知未就绪时悄悄改成无通知运行。

首次未配置时告知用户；取得本机部署授权后可执行 `harness task notify setup`，将原生权限提示交给用户处理。通知被禁用时交给用户决定是否开启，不擅自修改通知偏好、勿扰模式或安装登录项。通知/GUI 的开发测试只在既有 Sandbox 虚拟机中，不在宿主试弹窗。

## 2. 交出实际工作与结果校验

```sh
harness task start --title='Download resources' --cwd=/absolute/workdir \
  --verify='["python3","verify_download.py"]' \
  -- python3 download.py
```

- `--` 后是程序及参数，不是自动求值的 shell 字符串。确需管道时显式使用 `bash -lc`。
- 校验程序应检查真实目标产物；例如下载文件的预期路径、数量和大小，不能只返回 0，也不能把队列受理、进程退出当作完整成功。
- 优先复用现成业务校验。没有业务校验时必须说明只确认了命令退出；不能把未配置 `--verify` 的结果称为“业务已验证”。
- `--notify=none` 只能用于明确不需要通知的执行或非 GUI 测试，不是通知故障的自动降级。

## 3. 完成交接，不持续盯守

收到任务 ID、私有日志目录和 worker 状态后，把 ID、产物位置及“仍在后台运行”告知用户。工具会持久保存回执；其他任务记录只在当前记录策略或用户要求需要时维护，不因此强制创建仓库任务文件。

确认交接后结束本轮，或继续不依赖它的工作。不要为了维持通知反复调用工具，也不要把交接成功说成工作已完成。

## 4. 查询、区分失败并补发通知

```sh
harness task status <ID>
harness task list
harness task notify <ID>
```

- `starting`、`running`、`verifying` 都不是完成；`interrupted` 表示结果尚未确认，先核查副作用，不能盲目重跑。
- `succeeded` 要结合是否有业务校验解释；`failed` 应说明工作或校验失败，查看对应日志。
- 工作结果与 `notification.status` 分开判断。`accepted` 只代表系统受理，`presentInNotificationCenter` 只代表通知中心存在该通知；都不证明横幅实际显示或用户已读。
- 通知失败时，修复权限或通知后端后用 `harness task notify <ID>` **只补发通知，不重复执行工作**。

## 生命周期与交付边界

后台任务不依赖当前 agent/终端继续在线，但不提供跨退出登录、关机或重启的自动恢复。机器睡眠和勿扰设置也会影响通知时效；需要更强保证时先核对现有调度设施和授权，不自行扩大权限。

这条路径发送系统通知，不会主动发送聊天消息。报告实际任务结果、通知回执与尚未验证的部分；不能承诺用户一定看到或听到提醒。
