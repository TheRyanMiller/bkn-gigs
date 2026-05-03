from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scraper import config
from scraper.pipeline import r2


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_events() -> list[dict[str, Any]]:
    remote = r2.download_json(r2.public_key("events.json"), None)
    if isinstance(remote, list):
        return remote
    local = read_json(config.EVENTS_PATH, [])
    return local if isinstance(local, list) else []


def load_seen_cache() -> dict[str, dict[str, str]]:
    remote = r2.download_json(r2.state_key("seen-cache.json"), None)
    if isinstance(remote, dict):
        return remote
    local = read_json(config.SEEN_CACHE_PATH, {})
    return local if isinstance(local, dict) else {}


def write_outputs(
    *,
    events: list[dict[str, Any]],
    status: dict[str, Any],
    seen_cache: dict[str, dict[str, str]],
) -> None:
    write_json(config.EVENTS_PATH, events)
    write_json(config.STATUS_PATH, status)
    write_json(config.SEEN_CACHE_PATH, seen_cache)
    r2.upload_json(r2.public_key("events.json"), events)
    r2.upload_json(r2.public_key("scrape-status.json"), status)
    r2.upload_json(r2.state_key("seen-cache.json"), seen_cache)


def append_log(line: str) -> None:
    config.SCRAPE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with config.SCRAPE_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line.rstrip() + "\n")


def trim_log(max_lines: int = 5000) -> None:
    path = config.SCRAPE_LOG_PATH
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > max_lines:
        path.write_text("\n".join(lines[-max_lines:]) + "\n", encoding="utf-8")
    r2.upload_file(r2.state_key("scrape-log.txt"), path)

