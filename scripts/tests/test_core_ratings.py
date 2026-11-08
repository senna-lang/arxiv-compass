"""
scripts/core/ratings.py のユニットテスト

テスト対象:
- load_ratings: config から ratings を取得する（HTTP / ローカルファイル / 空リスト）
"""

import json
import os
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.ratings import load_ratings


class TestLoadRatings:
    def _make_config(self, output_dir: str, ratings_url: str = "") -> dict:
        return {"output_dir": output_dir, "ratings_url": ratings_url}

    def test_loads_from_local_file(self, tmp_path: Path):
        data = {"ratings": [{"id": "2301.00001", "rating": 3}]}
        ratings_file = tmp_path / "ratings.json"
        ratings_file.write_text(json.dumps(data), encoding="utf-8")

        config = self._make_config(str(tmp_path))
        result = load_ratings(config, root=tmp_path.parent)
        assert result == data["ratings"]

    def test_returns_empty_list_when_no_file(self, tmp_path: Path):
        config = self._make_config(str(tmp_path))
        result = load_ratings(config, root=tmp_path.parent)
        assert result == []

    def test_fetches_from_http_when_url_set(self, tmp_path: Path):
        ratings_data = {"ratings": [{"id": "2301.00002", "rating": 2}]}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(ratings_data).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        config = self._make_config(str(tmp_path), ratings_url="https://example.com/api/ratings")
        with patch("urllib.request.urlopen", return_value=mock_response):
            result = load_ratings(config, root=tmp_path.parent)

        assert result == ratings_data["ratings"]

    def test_falls_back_to_local_on_http_error(self, tmp_path: Path):
        data = {"ratings": [{"id": "2301.00003", "rating": 2}]}
        ratings_file = tmp_path / "ratings.json"
        ratings_file.write_text(json.dumps(data), encoding="utf-8")

        config = self._make_config(str(tmp_path), ratings_url="https://example.com/api/ratings")
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("network error")):
            result = load_ratings(config, root=tmp_path.parent)

        assert result == data["ratings"]

    def test_ratings_url_env_overrides_config(self, tmp_path: Path):
        body = {"ratings": [{"id": "2301.00004", "rating": 3}]}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(body).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        config = self._make_config(str(tmp_path), ratings_url="https://config.example/api/ratings")
        with (
            patch.dict(os.environ, {"RATINGS_URL": "https://env.example/api/ratings"}),
            patch("urllib.request.urlopen", return_value=mock_response) as opened,
        ):
            result = load_ratings(config, root=tmp_path.parent)
        opened.assert_called_once_with("https://env.example/api/ratings")
        assert result == body["ratings"]
