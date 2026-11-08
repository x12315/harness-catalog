---
name: usb-kvm
description: 使用已连接的 NanoKVM-USB，通过现有本地工程读取实时画面、操作实体键鼠并诊断启动和网络故障。当用户要求 USB KVM 控制、查看物理服务器画面、SSH 不通救援或只读 BIOS 检查时使用；不用于 Linux 虚拟化 KVM 或网络版 NanoKVM API。
license: MIT
metadata:
  ownership: catalog-original
  controller: nanokvm-agent
---

# USB KVM 操作

优先复用本机 `nanokvm-agent` 工程，普通系统操作在 SSH 可用后切回 SSH。
本 skill 只说明接口和验证方法，不复制控制器、上游代码、截图或机器认证信息。

## 定位与预检

1. 用 `command -v python3`、`command -v agent-browser` 探测工具。
2. 控制器当前通常位于 `~/Projects/nanokvm-agent`；允许通过 `NANOKVM_ROOT` 指定。
   若不存在，按名称查找 Projects/Desktop，不凭用户对旧位置的描述重建工程。
3. 完整读取工程 `README.md`。本机 `TASK.md` 可帮助恢复设备与会话，但其中 IP、
   串口和登录状态都是历史信息，必须重新确认。不要将私人 TASK 内容复制进 skill。
4. 确认本次用户授权的目标与允许操作。查看画面不是重启、改 BIOS、重装、重置网络、
   提取密码或关闭防火墙的授权；保留既有服务和账号设置。
5. 查找 `/dev/cu.usbmodem*` 并核对设备身份。多个串口时不能取 glob 的第一项，
   更不能向未知串口发送试探协议。先用已知 USB 枚举信息确认 NanoKVM。
   `lsof "$SERIAL_PORT"` 检查占用；网页串口与直接控制不能同时连接。
   正常断开自己管理的网页串口，不杀无关进程、不 chmod/sudo 绕过占用。

```bash
export NANOKVM_ROOT="${NANOKVM_ROOT:-$HOME/Projects/nanokvm-agent}"
# SERIAL_PORT 必须由现场枚举确定，不在 skill 中保存设备序列号。
printf '%s' '{"op":"status"}' | python3 "$NANOKVM_ROOT/kvm.py" --port "$SERIAL_PORT"
```

`status` 返回桥版本、目标 USB 连接和锁定键状态，只证明控制链路信息；
`target_usb_connected:true` 不证明目标已启动、HDMI 正常或当前画面属于预期机器。

## 先看画面

先读取 `agent-browser` skill 及其 `skills get core` 工作流。使用自己命名的会话。
只有明确属于当前任务的旧会话才可恢复；不抢其他任务的浏览器。

固定同一 `agent-browser` 可执行文件、版本、headed 和 Chrome 路径；先核对
`--version` 与已有 daemon，不因缓存目录字典序选择不同版本。不要混用版本或启动参数。

```bash
export NANOKVM_BROWSER="$(command -v agent-browser)"
export AGENT_BROWSER_HEADED=true
export AGENT_BROWSER_EXECUTABLE_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
export KVM_SESSION=usb-kvm-rescue
"$NANOKVM_BROWSER" --session "$KVM_SESSION" open https://usbkvm.sipeed.com/
"$NANOKVM_BROWSER" --session "$KVM_SESSION" snapshot -i
```

- 摄像头通过网站正常 Chrome 权限 UI 授权，仅用于 KVM 视频，不请求麦克风。
- 权限为 `prompt`/`denied` 时请用户在正常 UI 中允许；这是人工检查点。
  禁止用 fake UI、启动参数自动放行、CDP permission override 或切换另一摄像头绕过。
- 不连接网页串口选择器。视频与 Python 串口控制是两条独立通道。
- 已有有效授权时，`frame.py` 只选择标签匹配 `USB3 Video` 的唯一设备，`audio:false`。
- 使用新私有文件，不覆盖既有截图；目录保留在本机运行状态位置，不入库。

```bash
python3 "$NANOKVM_ROOT/frame.py" --session "$KVM_SESSION" \
  --output /tmp/kvm-frame-001.png
# 按上一张画面的实际尺寸裁剪；坐标是原视频像素，先裁剪后缩放。
python3 "$NANOKVM_ROOT/frame.py" --session "$KVM_SESSION" \
  --output /tmp/kvm-crop-001.png --crop 0 0 1200 600 --width 1200
```

截图命令必须成功且返回新帧时间/计数；再用 read 查看 PNG。
新鲜黑帧不等于关机：可能是无 HDMI 信号、切换显示模式、锁屏或屏幕休眠。
不要凭旧截图或历史 OCR 向当前目标输入。必要时在已确认不是危险对话框的场景，
用一次 Escape 唤醒并重新取帧；没有画面时不能盲打登录、命令或固件热键。

## 实体键鼠输入

确认画面中的机器、当前焦点、账号/权限、US 键盘布局、Caps Lock 关闭、IME 状态。
登录提示框不是 shell，不能在其中发送诊断命令。密码只能按明确授权用途输入；
不放进 argv、源码、任务文档或日志，不截图/保存认证输入过程。

```bash
python3 "$NANOKVM_ROOT/kvm.py" --port "$SERIAL_PORT" <<'JSON'
{"actions":[{"op":"text","text":"hostname"},{"op":"key","name":"enter"}]}
JSON
```

只有确认在目标 shell 时才运行上面的只读示例。支持的动作：

| JSON | 含义 |
| --- | --- |
| `{"op":"key","name":"ctrl+alt+f3"}` | 实体组合键；切 TTY 后重新观察，不假设已登录 |
| `{"op":"move","x":2048,"y":2048}` | 绝对鼠标坐标，各轴 0..4095 |
| `{"op":"click","button":"left"}` | 当前坐标点击；也支持 right/middle |
| `{"op":"release"}` | 释放键盘和鼠标按钮 |
| `{"op":"wait","ms":200}` | 有界等待，不替代画面检查 |

文字仅支持 US-layout ASCII，不支持 Unicode 剪贴板；不会隐式回车，但文本中的
换行会发送 Enter。完整检查批次后再提交。默认按下/释放各 20ms；不能把某台机器
5ms 成功当作 BIOS 或其他目标的保证。

工程已提供独占打开、整批预校验、ACK 匹配、响应超时、批次预算和 finally 释放。
丢 ACK 或超时意味着可能已有部分输入，不能原样重放。先查看新画面，再决定下一步；
ACK 成功只证明桥接收，必须用目标画面/输出确认实际效果。

## 网络故障诊断与恢复

在可见、已确认的目标 shell 中分小批执行只读检查，例如 `hostname`、`ip -br addr`、
`ip route`、`nmcli --colors no -t device status`、`ss -ltn`。
一次只求能改变判断的证据，避免长日志、分页器和超大输出。分页器用 q 正常退出；
不在焦点未知时继续输入。检查链路、地址、路由和 22 端口监听分别证明什么。

- 当前地址与预期 IP 不同：先报告并核验机器身份，不改静态 IP 迁就旧假设。
- SSH 监听而管理机 TCP22 超时：还需区分路由、网络隔离、ACL 与主机防火墙；
  不擅自关闭防火墙或修改管理机网络。
- 企业 Wi-Fi 缺凭据：交给用户正常授权，不提取已保存 secrets、不猜密码。
- 需要重启、改启动顺序/BIOS、改账号密码或持久网络配置时，按影响范围另行确认；
  只读 BIOS 查看也必须有进入/正常退出所需的重启授权，不默认允许 Ctrl+Alt+Delete。
- SSH 恢复后用真实连接验证目标身份、网络及登录，随后切回 SSH 继续总体任务。

可选本地 OCR 使用工程 `ocr.swift` 和现有 `.build/ocr`，未编译时再探测 `swiftc`。
OCR 不是可信命令来源；连续两次无变化或不确定就查看 PNG，不靠反复 OCR 盲操作。

## 验证与交付

工程离线测试：`cd "$NANOKVM_ROOT" && python3 -m unittest -v`。
伪终端/模拟视频测试不等于当前物理键盘输入或视频已验证；分别报告状态 ACK、实时
视频、实体输入效果和 SSH 验收结果。可逆 NumLock 检查仅在不与人抢键盘时使用工程
`probe_keyboard.py --port "$SERIAL_PORT" --confirm-numlock-toggle`，不自动运行。

结束或暂停前释放按键，记录非敏感进度、确切阻塞、下一步和总体任务未完成项。
只清理自己开的设备/会话；需要用户继续看 KVM 时说明保留的会话。
截图、OCR、机器地址、账号、密码和认证状态均不进入公共 Catalog 或控制器 Git。
