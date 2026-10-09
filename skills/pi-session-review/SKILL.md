---
name: pi-session-review
description: 读取本机及 SSH 主机上的 Pi session，去重 clone/fork 历史并复盘指定日期的工作时间线、主线、成果与循环瓶颈。当用户问今天/昨天做了什么、要求跨机器汇总 Pi 会话、日报复盘或分析时间利用率时使用。
license: MIT
compatibility: Requires Python 3; remote collection requires key-based SSH access.
allowed-tools: Bash Read
---

# Pi session review

以 **证据链** 复盘，而不是把所有用户提问都当成已完成工作。Pi session 位于各机器的 `~/.pi/agent/sessions/**/*.jsonl`。

## 1. 确定范围

把“今天”“昨天”转换成明确日期，并在结果中写出日期和时区。询问中明确给出的主机全部纳入；没有远端主机时只读本机。

远端仅使用已有的密钥认证：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 USER@HOST 'date "+%F %T %Z"'
```

连接失败时保留本机结果并明确缺口。不要读取或复制认证文件，也不要把密码放入命令。

## 2. 提取 session 证据

本机：

```bash
python3 skills/pi-session-review/scripts/extract_sessions.py --date YYYY-MM-DD > /tmp/pi-review-local.json
```

远端使用同一脚本，避免两台机器采用不同口径：

```bash
ssh -o BatchMode=yes USER@HOST 'python3 - --date YYYY-MM-DD' \
  < skills/pi-session-review/scripts/extract_sessions.py \
  > /tmp/pi-review-remote.json
```

脚本按 session entry 的 ISO 时间转换到机器本地时区，输出会话标题、工作目录、时间范围、用户消息和该会话当天最后一条文本结果。它会遮蔽常见密码/API key，并在单机内按 `timestamp + role + content` 去除 clone/fork 带来的重复历史；复盘中不要复述任何凭据。

读取生成的 JSON。数据量大时先用 Python 按小时或标题分组，不要直接截断最早或最晚部分。

**完成标准：** 每台可达机器都有提取结果，且报告独立用户消息数；不可达机器有明确错误。

## 3. 重建工作主线

跨机器再次按 `timestamp + role + content` 去重，然后按本地时间排序。聚类时综合：

- 会话标题与 `cwd`；
- 连续用户意图；
- assistant 最终结果中的验证、产物路径、数值和未完成项；
- 相邻任务之间的依赖关系。

把证据分为三类：

1. **意图**：用户要求、问题或假设；
2. **确认成果**：session 中明确报告了文件、测试、数据、发布或验证结果；
3. **缺口**：超时、待人工验证、远端不可达或只有计划没有结果。

不要从“请完成 X”推断 X 已完成。相同历史出现在多个 clone/fork 会话时只计算一次；分叉后新增内容仍分别保留。

## 4. 输出复盘

默认输出：

1. 日期、时区、数据来源与独立消息数；
2. 按时间排列的主线时间轴，注明机器；
3. 2–4 条真正的工作主线；
4. 当日确认成果与未闭环事项；
5. 若用户问效率，再指出循环中的等待、返工、决策门和可复用基础设施。

时间范围表示有证据的活跃窗口，不把两条消息之间的空白全部算作工作时长。对无法确认的完成状态使用“讨论了”“尝试了”或“记录显示”，而不是“完成了”。

**完成标准：** 时间轴覆盖当天全部独立消息簇，每条“已完成”都能追溯到 session 结果证据，clone/fork 重复不会夸大工作量。
