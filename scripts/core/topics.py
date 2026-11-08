"""Added topics. Separate basis; alpha does not zero them."""
import json, os, urllib.request
from pathlib import Path
from typing import Any
from core.config import ROOT as _DEFAULT_ROOT

def load_topics(config: dict[str, Any], root: Path = _DEFAULT_ROOT) -> list[dict[str, Any]]:
    url = os.environ.get("TOPICS_URL") or config.get("topics_url", "")
    path = root / config["output_dir"] / "topics.json"
    data = _fetch(url) if url else None
    if data is None:
        data = _read(path)
    return _clean((data or {}).get("topics", []))


def _fetch(url: str) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(url) as res:
            return json.loads(res.read())
    except Exception as e:
        print(f"[WARN] Failed to fetch topics from {url}: {e}")
        return None


def _read(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[WARN] Failed to read {path}: {e}")
        return None


def _clean(topics: list[Any]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for topic in topics:
        if not isinstance(topic, dict):
            continue
        text = str(topic.get("text", "")).strip()
        if text:
            cleaned.append({"text": text, "added_at": str(topic.get("added_at", ""))})
    return cleaned
