"""load_topics: local file, missing file, TOPICS_URL."""
import json
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.topics import load_topics


def _cfg(output_dir: str, topics_url: str = "") -> dict:
    return {"output_dir": output_dir, "topics_url": topics_url}


def test_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.delenv("TOPICS_URL", raising=False)
    assert load_topics(_cfg(str(tmp_path)), root=tmp_path.parent) == []


def test_reads_local_file(tmp_path, monkeypatch):
    monkeypatch.delenv("TOPICS_URL", raising=False)
    payload = {"topics": [{"text": "interpretability", "added_at": "t"}, {"text": "  ", "added_at": ""}]}
    (tmp_path / "topics.json").write_text(json.dumps(payload), encoding="utf-8")
    result = load_topics(_cfg(str(tmp_path)), root=tmp_path.parent)
    assert result == [{"text": "interpretability", "added_at": "t"}]


def test_topics_url_env_overrides_config(tmp_path, monkeypatch):
    monkeypatch.setenv("TOPICS_URL", "https://env.example/api/topics")
    body = {"topics": [{"text": "from-url", "added_at": ""}]}
    mock = MagicMock()
    mock.read.return_value = json.dumps(body).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock) as opened:
        result = load_topics(_cfg(str(tmp_path), "https://config.example/api/topics"), root=tmp_path.parent)
    opened.assert_called_once_with("https://env.example/api/topics")
    assert result == [{"text": "from-url", "added_at": ""}]
