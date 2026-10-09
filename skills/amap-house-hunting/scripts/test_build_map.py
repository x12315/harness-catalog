#!/usr/bin/env python3
"""Smoke-test offline map generation with fixed coordinates."""

import importlib.util
import json
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("build-map.py")
spec = importlib.util.spec_from_file_location("build_map", SCRIPT)
assert spec and spec.loader
build_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_map)


def main() -> None:
    """Verify deterministic ordering, escaping, and credential-free output."""
    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        plan = {
            "title": "西丽 <看房>",
            "city": "深圳市",
            "mode": "walk",
            "start": {"name": "起点", "location": "113.950000,22.580000"},
            "places": [
                {"name": "远处", "location": "113.970000,22.580000"},
                {"name": "近处", "location": "113.951000,22.580000"},
            ],
        }
        plan_path = root / "plan.json"
        output = root / "output"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        build_map.build(plan_path, output, skip_static_map=True)
        resolved = json.loads((output / "resolved-plan.json").read_text(encoding="utf-8"))
        generated_html = (output / "index.html").read_text(encoding="utf-8")
        assert [place["name"] for place in resolved["places"]] == ["近处", "远处"]
        assert "西丽 &lt;看房&gt;" in generated_html
        assert "AMAP_WEB_SERVICE_KEY" not in generated_html
        assert "uri.amap.com/navigation" in generated_html


if __name__ == "__main__":
    main()
