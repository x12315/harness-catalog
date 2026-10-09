#!/usr/bin/env python3
"""Extract one local calendar day from Pi JSONL sessions."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD, today, or yesterday")
    parser.add_argument(
        "--session-root",
        type=Path,
        default=Path.home() / ".pi" / "agent" / "sessions",
    )
    return parser.parse_args()


def target_date(value: str) -> date:
    today = datetime.now().astimezone().date()
    if value == "today":
        return today
    if value == "yesterday":
        return today - timedelta(days=1)
    return date.fromisoformat(value)


def local_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()


def redact_secrets(text: str) -> str:
    patterns = [
        r"(?i)\b(password|passwd)\s*[:：]?\s*\S+",
        r"(?i)(密码)\s*[:：]?\s*\S+",
        r"(?i)\b(sk-[a-z0-9_-]{12,})\b",
    ]
    for pattern in patterns:
        text = re.sub(pattern, lambda match: f"{match.group(1)}: [REDACTED]", text)
    return text


def text_content(content: Any) -> str:
    if isinstance(content, str):
        return redact_secrets(re.sub(r"\s+", " ", content).strip())
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif block.get("type") == "image":
            parts.append("[image]")
    return redact_secrets(re.sub(r"\s+", " ", " ".join(parts)).strip())


def assistant_text(message: dict[str, Any]) -> str:
    blocks = message.get("content", [])
    if not isinstance(blocks, list):
        return ""
    return redact_secrets(
        re.sub(
            r"\s+",
            " ",
            " ".join(
                block.get("text", "")
                for block in blocks
                if isinstance(block, dict) and block.get("type") == "text"
            ),
        ).strip()
    )


def extract(path: Path, day: date) -> dict[str, Any] | None:
    header: dict[str, Any] = {}
    name = ""
    entries: list[tuple[datetime, str, str]] = []

    try:
        with path.open(errors="replace") as source:
            for line in source:
                entry = json.loads(line)
                if entry.get("type") == "session":
                    header = entry
                elif entry.get("type") == "session_info":
                    name = entry.get("name", "")

                timestamp = entry.get("timestamp")
                message = entry.get("message", {})
                if not timestamp or entry.get("type") != "message":
                    continue
                when = local_datetime(timestamp)
                if when.date() != day:
                    continue
                role = message.get("role")
                if role == "user":
                    text = text_content(message.get("content", ""))
                elif role == "assistant":
                    text = assistant_text(message)
                else:
                    continue
                if text:
                    entries.append((when, role, text))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return {"path": str(path), "error": str(error)}

    if not entries:
        return None

    users = [
        {"timestamp": when.isoformat(), "text": text}
        for when, role, text in entries
        if role == "user"
    ]
    assistant_results = [
        {"timestamp": when.isoformat(), "text": text[-4000:]}
        for when, role, text in entries
        if role == "assistant"
    ]
    return {
        "path": str(path),
        "session_id": header.get("id"),
        "name": name,
        "cwd": header.get("cwd", ""),
        "first_activity": min(item[0] for item in entries).isoformat(),
        "last_activity": max(item[0] for item in entries).isoformat(),
        "user_messages": users,
        "last_assistant_result": assistant_results[-1] if assistant_results else None,
    }


def main() -> None:
    args = parse_args()
    day = target_date(args.date)
    sessions = []
    errors = []
    for path in sorted(args.session_root.rglob("*.jsonl")):
        result = extract(path, day)
        if not result:
            continue
        if "error" in result:
            errors.append(result)
        else:
            sessions.append(result)

    seen: set[tuple[str, str, str]] = set()
    unique_users = []
    for session in sessions:
        for message in session["user_messages"]:
            key = (message["timestamp"], "user", message["text"])
            if key in seen:
                continue
            seen.add(key)
            unique_users.append(message)
    unique_users.sort(key=lambda item: item["timestamp"])

    now = datetime.now().astimezone()
    print(
        json.dumps(
            {
                "date": day.isoformat(),
                "timezone": str(now.tzinfo),
                "session_root": str(args.session_root),
                "session_count": len(sessions),
                "unique_user_message_count": len(unique_users),
                "unique_user_messages": unique_users,
                "sessions": sessions,
                "errors": errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
