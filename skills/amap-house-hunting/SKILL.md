---
name: amap-house-hunting
description: Builds an AMap-based viewing map and ordered itinerary from rental or property candidates. Use when planning apartment viewings, marking candidate homes, resolving Chinese addresses, or generating sequential AMap navigation links.
compatibility: Requires Python 3; unresolved places and static maps require an AMap Web Service key in AMAP_WEB_SERVICE_KEY or the macOS login keychain.
---

# 高德看房地图

把房源位置、路线顺序和逐站导航做成一个本地 HTML。流程使用脚本和高德 Web 服务 API，不需要 MCP，也不保存 API Key。

## 1. 收集地点

将计划写到仓库外的 JSON 文件。优先使用房源详情里的完整地址或高德坐标；名称可能重名时用 `query`，让脚本列出候选结果。

```json
{
  "title": "西丽看房",
  "city": "深圳市",
  "mode": "walk",
  "start": {"name": "大疆天空之城", "query": "大疆天空之城"},
  "places": [
    {"name": "示例公寓", "address": "深圳市南山区……"},
    {"name": "另一套房", "location": "113.950000,22.580000"}
  ]
}
```

`mode` 可用 `walk`、`drive`、`bus` 或 `ride`。预约时间、租金、联系人等任意附加字段会进入已解析 JSON，但不要写身份证、门禁密码或其他敏感信息。

**完成条件：** 起点和每套房源各有 `address`、`query` 或 `location`。

## 2. 只在需要时配置高德

只要有地点缺少 `location`，或需要下载高德静态地图，就需要高德开放平台的“Web 服务”Key：

1. 在 <https://console.amap.com/dev/key/app> 创建应用；
2. 添加 Key，服务平台选择“Web 服务”；
3. 不在聊天、计划 JSON 或仓库中记录 Key。macOS 上优先存入登录钥匙串；下面的命令会在终端中安全提示输入：

```bash
security add-generic-password -U -a "$USER" -s amap-house-hunting -w
```

也可以只在启动 agent 的 shell 中设置：

```bash
export AMAP_WEB_SERVICE_KEY='...'
```

已有全部坐标时，可以用 `--skip-static-map` 无 Key 生成清单和导航链接。

**完成条件：** 钥匙串存在 `amap-house-hunting` 条目，或 `test -n "$AMAP_WEB_SERVICE_KEY"` 成功；若跳过静态地图，则输入中的每个地点已有坐标。

## 3. 生成并消歧

从 skill 目录运行：

```bash
python3 scripts/build-map.py /path/to/plan.json /path/to/output
```

脚本只自动接受唯一的精确名称匹配。遇到同名地点时会写出 `output/candidates.json` 并退出；核对行政区和地址后，把正确候选的 `location` 复制回计划 JSON，再重新运行。不要根据列表顺序猜测。

脚本以起点为基准，用直线距离的最近邻顺序安排未固定时间的房源。已有预约时间时，由 agent 先按预约约束调整输入顺序；最近邻只是本地启发式，不代表实时路况。

不必一趟看完时，给每个地点设置相同的 `trip` 分组和组内 `trip_order`。每组首个地点可带 `trip_title`、`trip_note`；每一段用 `leg_mode` 标注 `walk`、`ride`、`drive` 或 `bus`。地图会用不同颜色画出每趟路线，并让每趟都从起点重新出发。

**完成条件：** 输出目录存在 `index.html`、`resolved-plan.json`，未使用 `--skip-static-map` 时还存在 `map.png`。

## 4. 交付与现场使用

打开 `index.html` 检查每个编号、名称和地址。手机查看时，每站点击“高德导航”；导航链接不含 API Key。将错位地点改为高德分享页显示的明确坐标后重建。

**完成条件：** 所有点位经用户确认，逐站链接能在高德中打开，路线没有违反预约时间。
