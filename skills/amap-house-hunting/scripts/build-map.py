#!/usr/bin/env python3
"""Build a local AMap viewing map and sequential navigation itinerary."""

from __future__ import annotations

import argparse
import getpass
import html
import itertools
import json
import math
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_ROOT = "https://restapi.amap.com/v3"
MODES = {"walk", "drive", "bus", "ride"}


class MapBuildError(Exception):
    """Report an actionable map-input or AMap API failure."""


def load_api_key() -> str | None:
    """Load the AMap key from the environment or the macOS login keychain."""
    if key := os.environ.get("AMAP_WEB_SERVICE_KEY"):
        return key
    if not shutil.which("security"):
        return None
    result = subprocess.run(
        ["security", "find-generic-password", "-a", getpass.getuser(), "-s", "amap-house-hunting", "-w"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def request_json(endpoint: str, parameters: dict[str, str], key: str) -> dict[str, Any]:
    """Return one AMap Web Service response without logging the credential."""
    query = urllib.parse.urlencode({**parameters, "key": key, "output": "JSON"})
    request = urllib.request.Request(f"{API_ROOT}/{endpoint}?{query}", headers={"User-Agent": "amap-house-hunting/1"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except (OSError, json.JSONDecodeError) as error:
        raise MapBuildError(f"高德请求失败：{error}") from error
    if payload.get("status") != "1":
        raise MapBuildError(f"高德返回错误：{payload.get('info', 'unknown error')}")
    return payload


def parse_location(value: str) -> tuple[float, float]:
    """Parse an AMap GCJ-02 `longitude,latitude` coordinate."""
    try:
        longitude, latitude = (float(part.strip()) for part in value.split(",", 1))
    except (TypeError, ValueError) as error:
        raise MapBuildError(f"坐标格式应为 longitude,latitude：{value!r}") from error
    if not (73 <= longitude <= 136 and 3 <= latitude <= 54):
        raise MapBuildError(f"坐标不在中国常用范围内：{value!r}")
    return longitude, latitude


def normalized_name(value: str) -> str:
    """Normalize punctuation and spacing for conservative POI-name matching."""
    return "".join(character.lower() for character in value if character.isalnum())


def poi_candidates(point: dict[str, Any], city: str, key: str) -> list[dict[str, str]]:
    """Search AMap and return compact candidates suitable for human disambiguation."""
    query = str(point.get("query") or point.get("name") or "").strip()
    payload = request_json(
        "place/text",
        {"keywords": query, "city": city, "citylimit": "true", "offset": "10", "page": "1", "extensions": "base"},
        key,
    )
    return [
        {
            "name": str(poi.get("name", "")),
            "address": str(poi.get("address", "")),
            "district": str(poi.get("adname", "")),
            "location": str(poi.get("location", "")),
        }
        for poi in payload.get("pois", [])
        if poi.get("location")
    ]


def geocode_address(point: dict[str, Any], city: str, key: str) -> list[dict[str, str]]:
    """Geocode a full street address into compact human-reviewable candidates."""
    address = str(point["address"]).strip()
    payload = request_json("geocode/geo", {"address": address, "city": city}, key)
    return [
        {
            "name": str(point.get("name", address)),
            "address": str(result.get("formatted_address", address)),
            "district": str(result.get("district", "")),
            "location": str(result.get("location", "")),
        }
        for result in payload.get("geocodes", [])
        if result.get("location")
    ]


def resolve_point(point: dict[str, Any], city: str, key: str | None) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Resolve one point only when its coordinates or API result are unambiguous."""
    resolved = dict(point)
    if point.get("location"):
        longitude, latitude = parse_location(str(point["location"]))
        resolved["location"] = f"{longitude:.6f},{latitude:.6f}"
        return resolved, []
    if not key:
        raise MapBuildError(f"“{point.get('name', '未命名地点')}”缺少坐标；请设置 AMAP_WEB_SERVICE_KEY")

    candidates = geocode_address(point, city, key) if point.get("address") else poi_candidates(point, city, key)
    if point.get("address") and len(candidates) == 1:
        selected = candidates[0]
    else:
        wanted = normalized_name(str(point.get("name") or point.get("query") or ""))
        exact = [candidate for candidate in candidates if normalized_name(candidate["name"]) == wanted]
        if len(exact) != 1:
            return None, candidates
        selected = exact[0]
    resolved["location"] = selected["location"]
    resolved.setdefault("address", selected["address"])
    resolved["district"] = selected["district"]
    return resolved, []


def distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Return approximate great-circle distance in kilometres."""
    lon1, lat1 = parse_location(first["location"])
    lon2, lat2 = parse_location(second["location"])
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    value = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 6371.0 * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def nearest_neighbour_order(start: dict[str, Any], places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order places with a deterministic nearest-neighbour heuristic."""
    remaining = list(enumerate(places))
    ordered: list[dict[str, Any]] = []
    current = start
    while remaining:
        chosen = min(remaining, key=lambda item: (distance(current, item[1]), item[0]))
        remaining.remove(chosen)
        ordered.append(chosen[1])
        current = chosen[1]
    return ordered


def navigation_url(destination: dict[str, Any], mode: str) -> str:
    """Build an AMap URI that navigates from the phone's live location."""
    parameters = {
        "to": f"{destination['location']},{destination['name']}",
        "mode": mode,
        "policy": "1",
        "src": "amap-house-hunting",
        "callnative": "1",
    }
    return "https://uri.amap.com/navigation?" + urllib.parse.urlencode(parameters)


def map_zoom(points: list[dict[str, Any]]) -> int:
    """Choose a conservative static-map zoom that contains the point spread."""
    coordinates = [parse_location(point["location"]) for point in points]
    span = max(max(value[index] for value in coordinates) - min(value[index] for value in coordinates) for index in (0, 1))
    for threshold, zoom in ((0.005, 16), (0.01, 15), (0.02, 14), (0.05, 13), (0.1, 12), (0.2, 11), (0.5, 10)):
        if span <= threshold:
            return zoom
    return 9


def download_static_map(start: dict[str, Any], places: list[dict[str, Any]], output: Path, key: str) -> None:
    """Download a credential-free-at-rest PNG overview from AMap."""
    all_points = [start, *places]
    coordinates = [parse_location(point["location"]) for point in all_points]
    center = f"{(min(p[0] for p in coordinates) + max(p[0] for p in coordinates)) / 2:.6f},{(min(p[1] for p in coordinates) + max(p[1] for p in coordinates)) / 2:.6f}"
    grouped_places = [list(group) for _, group in itertools.groupby(places, key=lambda point: point.get("trip", 1))]
    colors = ("0xE5484D", "0x1677FF", "0x2E9B64", "0x8F5BD7")
    paths = "|".join(
        f"6,{colors[index % len(colors)]},1,,0.7:{start['location']};"
        + ";".join(point["location"] for point in group)
        for index, group in enumerate(grouped_places)
    )
    markers = "|".join([
        f"large,0xE5484D,0:{start['location']}",
        *(f"mid,0x1677FF,{index}:{point['location']}" for index, point in enumerate(places, 1)),
    ])
    parameters = [
        ("location", center),
        ("zoom", str(map_zoom(all_points))),
        ("size", "1024*700"),
        ("scale", "2"),
        ("markers", markers),
        ("paths", paths),
        ("key", key),
    ]
    request = urllib.request.Request(
        "https://restapi.amap.com/v3/staticmap?" + urllib.parse.urlencode(parameters),
        headers={"User-Agent": "amap-house-hunting/1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get_content_type()
            content = response.read()
    except OSError as error:
        raise MapBuildError(f"静态地图下载失败：{error}") from error
    if not content_type.startswith("image/"):
        raise MapBuildError("高德没有返回地图图片；请检查 Web 服务 Key 的权限和额度")
    output.write_bytes(content)


def render_html(plan: dict[str, Any], map_available: bool) -> str:
    """Render the resolved route as a mobile-friendly local HTML page."""
    start = plan["start"]
    mode_labels = {"walk": "步行", "ride": "骑行", "drive": "驾车/打车", "bus": "公交"}
    sections = []
    numbered_places = list(enumerate(plan["places"], 1))
    for _, grouped_items in itertools.groupby(numbered_places, key=lambda item: item[1].get("trip", 1)):
        items = list(grouped_items)
        first_place = items[0][1]
        title = html.escape(str(first_place.get("trip_title", "一次看房行程")))
        note = html.escape(str(first_place.get("trip_note", "")))
        cards = []
        for index, place in items:
            leg_mode = str(place.get("leg_mode", plan["mode"]))
            link = navigation_url(place, leg_mode)
            metadata = [
                f"<span>{html.escape(str(place[field]))}</span>"
                for field in ("rent", "appointment", "contact", "notes")
                if place.get(field)
            ]
            cards.append(
                f"<li><b>{index}. {html.escape(str(place['name']))}</b> <em>{mode_labels.get(leg_mode, leg_mode)}</em>"
                f"<p>{html.escape(str(place.get('address') or place.get('district') or place['location']))}</p>"
                f"<div>{''.join(metadata)}</div><a href=\"{html.escape(link)}\">用当前位置导航到：{html.escape(str(place['name']))}</a></li>"
            )
        sections.append(f"<section><h2>{title}</h2><p class=\"trip-note\">{note}</p><ol>{''.join(cards)}</ol></section>")
    map_markup = '<img src="map.png" alt="高德看房点位与路线概览">' if map_available else '<p class="notice">本次跳过静态地图，仅生成路线清单。</p>'
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(str(plan['title']))}</title><style>
body{{font:16px/1.5 system-ui,sans-serif;margin:auto;max-width:820px;padding:20px;background:#f5f5f3;color:#222}}h1{{margin-bottom:4px}}h2{{margin:28px 0 2px}}img{{width:100%;border-radius:14px}}ol{{padding:0;list-style:none}}li{{background:white;margin:12px 0;padding:16px;border-radius:12px;box-shadow:0 1px 4px #0001}}li p,.trip-note{{color:#666;margin:6px 0}}li span{{margin-right:12px}}em{{font-style:normal;font-size:13px;background:#e8f1ff;color:#075dcc;padding:3px 8px;border-radius:20px}}a{{display:inline-block;margin-top:10px;color:#075dcc;font-weight:600}}.notice{{padding:20px;background:#fff4d6;border-radius:12px}}
</style></head><body><h1>{html.escape(str(plan['title']))}</h1><p>起点：{html.escape(str(start['name']))} · 已拆成多次轻松看房，不必一天跑完。</p>{map_markup}{''.join(sections)}</body></html>"""


def build(plan_path: Path, output_directory: Path, skip_static_map: bool) -> None:
    """Resolve a plan, order its stops, and write the complete local artifact."""
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MapBuildError(f"无法读取计划：{error}") from error
    if not isinstance(plan.get("places"), list) or not plan.get("places") or not isinstance(plan.get("start"), dict):
        raise MapBuildError("计划必须包含 start 对象和非空 places 数组")
    mode = str(plan.get("mode", "walk"))
    if mode not in MODES:
        raise MapBuildError(f"mode 必须是 {', '.join(sorted(MODES))} 之一")

    output_directory.mkdir(parents=True, exist_ok=True)
    key = load_api_key()
    unresolved: dict[str, list[dict[str, str]]] = {}
    start, candidates = resolve_point(plan["start"], str(plan.get("city", "")), key)
    if start is None:
        unresolved[str(plan["start"].get("name", "起点"))] = candidates
    resolved_places = []
    for place in plan["places"]:
        resolved, candidates = resolve_point(place, str(plan.get("city", "")), key)
        if resolved is None:
            unresolved[str(place.get("name", "未命名地点"))] = candidates
        else:
            resolved_places.append(resolved)
    if unresolved:
        candidates_path = output_directory / "candidates.json"
        candidates_path.write_text(json.dumps(unresolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise MapBuildError(f"存在同名或无精确匹配地点；请核对 {candidates_path} 并把正确 location 写回计划")
    assert start is not None

    if any(place.get("trip") is not None for place in resolved_places):
        if not all(place.get("trip") is not None for place in resolved_places):
            raise MapBuildError("使用分趟计划时，每个地点都必须设置 trip")
        ordered_places = sorted(resolved_places, key=lambda place: (place["trip"], place.get("trip_order", 0)))
    else:
        ordered_places = nearest_neighbour_order(start, resolved_places)
    resolved_plan = {
        **plan,
        "title": str(plan.get("title", "看房地图")),
        "mode": mode,
        "start": start,
        "places": ordered_places,
    }
    map_available = not skip_static_map
    if map_available:
        if not key:
            raise MapBuildError("下载高德静态地图需要 AMAP_WEB_SERVICE_KEY；或使用 --skip-static-map")
        download_static_map(start, resolved_plan["places"], output_directory / "map.png", key)
    (output_directory / "resolved-plan.json").write_text(json.dumps(resolved_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_directory / "index.html").write_text(render_html(resolved_plan, map_available), encoding="utf-8")


def main() -> int:
    """Run the command-line map builder."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--skip-static-map", action="store_true")
    arguments = parser.parse_args()
    try:
        build(arguments.plan, arguments.output, arguments.skip_static_map)
    except MapBuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(arguments.output / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
