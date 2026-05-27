"""Tests for the 4 Zhihu skill scripts.

Uses importlib to dynamically import standalone scripts and
unittest.mock to stub urllib.request.urlopen — no real API calls.
"""

from __future__ import annotations

import importlib.util
import json
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Dynamic module loading helpers
# ---------------------------------------------------------------------------

_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills"


def _load_module(name: str, path: Path):
    """Load a standalone script as a Python module via importlib."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load all 4 skill modules once at module scope
zhihu_search = _load_module(
    "zhihu_search", _SKILLS_DIR / "zhihu-search" / "scripts" / "zhihu-search.py"
)
global_search = _load_module(
    "global_search",
    _SKILLS_DIR / "zhihu-global-search" / "scripts" / "global-search.py",
)
zhida = _load_module("zhida", _SKILLS_DIR / "zhihu-zhida" / "scripts" / "zhida.py")
hot_list = _load_module(
    "hot_list", _SKILLS_DIR / "zhihu-hot-list" / "scripts" / "hot-list.py"
)


# ---------------------------------------------------------------------------
# Fixtures: fake urllib responses
# ---------------------------------------------------------------------------


def _fake_urlopen_bytes(body: bytes, status: int = 200):
    """Return a context-manager mock whose .read() returns *body*."""
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=cm)
    cm.__exit__ = MagicMock(return_value=False)
    cm.read.return_value = body
    cm.status = status
    cm.headers = {}
    return cm


def _fake_urlopen_http_error(code: int, body: bytes = b"{}"):
    """Return an HTTPError raised inside urlopen."""
    from urllib.error import HTTPError

    err = HTTPError(
        url="https://example.com",
        code=code,
        msg="Error",
        hdrs={},
        fp=BytesIO(body),
    )
    return err


# ===================================================================
# zhihu-search
# ===================================================================


class TestZhihuSearch:
    """Tests for .agents/skills/zhihu-search/scripts/zhihu-search.py"""

    # --- parse_payload / parse_query / parse_count ---

    def test_parse_payload_valid(self):
        data = zhihu_search.parse_payload('{"query":"test","count":5}')
        assert data["query"] == "test"
        assert data["count"] == 5

    def test_parse_payload_invalid_json(self):
        with pytest.raises(SystemExit):
            zhihu_search.parse_payload("not json")

    def test_parse_payload_non_dict(self):
        with pytest.raises(SystemExit):
            zhihu_search.parse_payload("[1,2,3]")

    def test_parse_query_valid(self):
        assert zhihu_search.parse_query({"query": "  hello  "}) == "hello"

    def test_parse_query_missing(self):
        with pytest.raises(SystemExit):
            zhihu_search.parse_query({})

    def test_parse_count_clamp(self):
        assert zhihu_search.parse_count({"count": 99}) == 10
        assert zhihu_search.parse_count({"count": -1}) == 1
        assert zhihu_search.parse_count({"count": 5}) == 5

    def test_parse_count_default(self):
        assert zhihu_search.parse_count({}) == 10

    # --- build_result ---

    def test_build_result_normal(self):
        api_resp = {
            "Code": 0,
            "Message": "ok",
            "Data": {
                "Items": [
                    {
                        "Title": "T1",
                        "Url": "https://example.com",
                        "AuthorName": "A",
                        "ContentText": "summary",
                        "VoteUpCount": 10,
                        "CommentCount": 2,
                        "EditTime": 1234,
                    }
                ]
            },
        }
        result = zhihu_search.build_result(api_resp)
        assert result["code"] == 0
        assert result["item_count"] == 1
        assert result["items"][0]["title"] == "T1"
        assert result["items"][0]["vote_up_count"] == 10

    def test_build_result_empty_data(self):
        result = zhihu_search.build_result({})
        assert result["code"] == -1
        assert result["item_count"] == 0
        assert result["items"] == []

    # --- get_endpoint ---

    def test_get_endpoint_default(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_ZHIHU_SEARCH_URL", raising=False)
        monkeypatch.delenv("ZHIHU_OPENAPI_BASE_URL", raising=False)
        url = zhihu_search.get_endpoint()
        assert url == "https://developer.zhihu.com/api/v1/content/zhihu_search"

    def test_get_endpoint_custom_base(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_ZHIHU_SEARCH_URL", raising=False)
        monkeypatch.setenv("ZHIHU_OPENAPI_BASE_URL", "https://custom.host")
        url = zhihu_search.get_endpoint()
        assert url == "https://custom.host/api/v1/content/zhihu_search"

    def test_get_endpoint_explicit_override(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ZHIHU_SEARCH_URL", "https://override/search")
        url = zhihu_search.get_endpoint()
        assert url == "https://override/search"

    # --- request_zhihu: missing token ---

    def test_request_zhihu_missing_secret(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_ACCESS_SECRET", raising=False)
        with pytest.raises(SystemExit):
            zhihu_search.request_zhihu("test", 5)

    # --- request_zhihu: successful API response ---

    def test_request_zhihu_success(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        resp_body = json.dumps(
            {"Code": 0, "Message": "ok", "Data": {"Items": []}}
        ).encode()
        with patch.object(
            zhihu_search, "urlopen", return_value=_fake_urlopen_bytes(resp_body)
        ):
            result = zhihu_search.request_zhihu("hello", 3)
        assert result["Code"] == 0

    # --- request_zhihu: HTTP error ---

    def test_request_zhihu_http_error(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        err = _fake_urlopen_http_error(403, b'{"error":"forbidden"}')
        with (
            patch.object(zhihu_search, "urlopen", side_effect=err),
            pytest.raises(SystemExit),
        ):
            zhihu_search.request_zhihu("hello", 3)

    # --- request_zhihu: network / timeout error ---

    def test_request_zhihu_timeout(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        from urllib.error import URLError

        with (
            patch.object(zhihu_search, "urlopen", side_effect=URLError("timeout")),
            pytest.raises(SystemExit),
        ):
            zhihu_search.request_zhihu("hello", 3)


# ===================================================================
# global-search
# ===================================================================


class TestGlobalSearch:
    """Tests for .agents/skills/zhihu-global-search/scripts/global-search.py"""

    # --- parse_filter / parse_search_db ---

    def test_parse_filter_valid(self):
        assert (
            global_search.parse_filter({"filter": 'host=="example.com"'})
            == 'host=="example.com"'
        )

    def test_parse_filter_empty(self):
        assert global_search.parse_filter({}) == ""

    def test_parse_filter_non_string(self):
        with pytest.raises(SystemExit):
            global_search.parse_filter({"filter": 123})

    def test_parse_search_db_valid(self):
        assert global_search.parse_search_db({"search_db": "all"}) == "all"
        assert global_search.parse_search_db({"search_db": "REALTIME"}) == "realtime"

    def test_parse_search_db_invalid(self):
        with pytest.raises(SystemExit):
            global_search.parse_search_db({"search_db": "unknown"})

    def test_parse_search_db_empty(self):
        assert global_search.parse_search_db({}) == ""

    # --- normalize_items ---

    def test_normalize_items_normal(self):
        api_resp = {
            "Code": 0,
            "Message": "ok",
            "Data": {
                "Items": [
                    {
                        "Title": "G1",
                        "Url": "https://example.com",
                        "AuthorName": "B",
                        "ContentText": "desc",
                        "EditTime": 999,
                    }
                ]
            },
        }
        result = global_search.normalize_items(api_resp)
        assert result["code"] == 0
        assert result["item_count"] == 1
        assert result["items"][0]["title"] == "G1"

    def test_normalize_items_empty(self):
        result = global_search.normalize_items({})
        assert result["code"] == -1
        assert result["items"] == []

    # --- get_endpoint ---

    def test_get_endpoint_default(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_GLOBAL_SEARCH_URL", raising=False)
        monkeypatch.delenv("ZHIHU_OPENAPI_BASE_URL", raising=False)
        url = global_search.get_endpoint()
        assert url == "https://developer.zhihu.com/api/v1/content/global_search"

    # --- request_global_search: missing token ---

    def test_request_missing_secret(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_ACCESS_SECRET", raising=False)
        with pytest.raises(SystemExit):
            global_search.request_global_search("test", 10, "", "")

    # --- request_global_search: success ---

    def test_request_success(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        resp_body = json.dumps(
            {"Code": 0, "Message": "ok", "Data": {"Items": []}}
        ).encode()
        with patch.object(
            global_search, "urlopen", return_value=_fake_urlopen_bytes(resp_body)
        ):
            result = global_search.request_global_search("hello", 5, "", "all")
        assert result["Code"] == 0

    # --- request_global_search: HTTP error ---

    def test_request_http_error(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        err = _fake_urlopen_http_error(500, b'{"error":"internal"}')
        with (
            patch.object(global_search, "urlopen", side_effect=err),
            pytest.raises(SystemExit),
        ):
            global_search.request_global_search("hello", 5, "", "")

    # --- parse_count: clamped to 20 max ---

    def test_parse_count_clamp(self):
        assert global_search.parse_count({"count": 100}) == 20
        assert global_search.parse_count({"count": 0}) == 1


# ===================================================================
# zhida
# ===================================================================


class TestZhida:
    """Tests for .agents/skills/zhihu-zhida/scripts/zhida.py"""

    # --- build_request_body ---

    def test_build_request_body_valid(self):
        payload = {
            "model": "zhida-thinking-1p5",
            "messages": [{"role": "user", "content": "hello"}],
        }
        body = zhida.build_request_body(payload)
        assert body["model"] == "zhida-thinking-1p5"
        assert len(body["messages"]) == 1

    def test_build_request_body_missing_model(self):
        with pytest.raises(SystemExit):
            zhida.build_request_body({"messages": [{"role": "user", "content": "x"}]})

    def test_build_request_body_missing_messages(self):
        with pytest.raises(SystemExit):
            zhida.build_request_body({"model": "zhida-thinking-1p5"})

    def test_build_request_body_empty_messages(self):
        with pytest.raises(SystemExit):
            zhida.build_request_body({"model": "zhida-thinking-1p5", "messages": []})

    # --- normalize_non_stream ---

    def test_normalize_non_stream_normal(self):
        payload = {
            "id": "chat-123",
            "model": "zhida-thinking-1p5",
            "choices": [
                {
                    "message": {
                        "content": "answer text",
                        "reasoning_content": "thinking...",
                    },
                    "finish_reason": "stop",
                }
            ],
        }
        result = zhida.normalize_non_stream(payload)
        assert result["code"] == 0
        assert result["content"] == "answer text"
        assert result["reasoning_content"] == "thinking..."
        assert result["finish_reason"] == "stop"

    def test_normalize_non_stream_empty_choices(self):
        result = zhida.normalize_non_stream({"id": "x", "model": "m", "choices": []})
        assert result["content"] == ""
        assert result["code"] == 0

    # --- auth_headers: missing token ---

    def test_auth_headers_missing_secret(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_ACCESS_SECRET", raising=False)
        with pytest.raises(SystemExit):
            zhida.auth_headers()

    # --- auth_headers: success ---

    def test_auth_headers_success(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "my-secret")
        headers = zhida.auth_headers()
        assert headers["Authorization"] == "Bearer my-secret"
        assert "Content-Type" in headers
        assert "X-Request-Timestamp" in headers

    # --- get_endpoint ---

    def test_get_endpoint_default(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_ZHIDA_URL", raising=False)
        monkeypatch.delenv("ZHIHU_OPENAPI_BASE_URL", raising=False)
        url = zhida.get_endpoint()
        assert url == "https://developer.zhihu.com/v1/chat/completions"

    # --- post_json: success ---

    def test_post_json_success(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        resp_body = json.dumps({"id": "1", "model": "m", "choices": []}).encode()
        mock_cm = _fake_urlopen_bytes(resp_body, status=200)
        with patch.object(zhida, "urlopen", return_value=mock_cm):
            status, _headers, body = zhida.post_json({"model": "m", "messages": []})
        assert status == 200
        parsed = json.loads(body)
        assert parsed["id"] == "1"

    # --- post_json: HTTP error ---

    def test_post_json_http_error(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        err = _fake_urlopen_http_error(429, b'{"error":"rate limit"}')
        with patch.object(zhida, "urlopen", side_effect=err), pytest.raises(SystemExit):
            zhida.post_json({"model": "m", "messages": []})

    # --- post_json: timeout ---

    def test_post_json_timeout(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        from urllib.error import URLError

        with (
            patch.object(zhida, "urlopen", side_effect=URLError("timeout")),
            pytest.raises(SystemExit),
        ):
            zhida.post_json({"model": "m", "messages": []})

    # --- parse_http_error_body ---

    def test_parse_http_error_body_json(self):
        result = zhida.parse_http_error_body('{"detail":"bad"}')
        assert result["detail"] == "bad"

    def test_parse_http_error_body_plain(self):
        result = zhida.parse_http_error_body("not json")
        assert result == "not json"


# ===================================================================
# hot-list
# ===================================================================


class TestHotList:
    """Tests for .agents/skills/zhihu-hot-list/scripts/hot-list.py"""

    # --- parse_payload ---

    def test_parse_payload_valid(self):
        data = hot_list.parse_payload('{"limit":10}')
        assert data["limit"] == 10

    def test_parse_payload_empty_string(self):
        result = hot_list.parse_payload("")
        assert result == {}

    def test_parse_payload_whitespace(self):
        result = hot_list.parse_payload("   ")
        assert result == {}

    def test_parse_payload_invalid_json(self):
        with pytest.raises(SystemExit):
            hot_list.parse_payload("not json")

    # --- parse_limit ---

    def test_parse_limit_clamp(self):
        assert hot_list.parse_limit({"limit": 999}) == 30
        assert hot_list.parse_limit({"limit": 0}) == 1
        assert hot_list.parse_limit({"limit": 10}) == 10

    def test_parse_limit_default(self):
        assert hot_list.parse_limit({}) == 30

    # --- get_endpoint ---

    def test_get_endpoint_default(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_HOT_LIST_URL", raising=False)
        monkeypatch.delenv("ZHIHU_OPENAPI_BASE_URL", raising=False)
        url = hot_list.get_endpoint()
        assert url == "https://developer.zhihu.com/api/v1/content/hot_list"

    def test_get_endpoint_explicit(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_HOT_LIST_URL", "https://custom/hot")
        url = hot_list.get_endpoint()
        assert url == "https://custom/hot"

    # --- request_hot_list: missing token ---

    def test_request_missing_secret(self, monkeypatch):
        monkeypatch.delenv("ZHIHU_ACCESS_SECRET", raising=False)
        with pytest.raises(SystemExit):
            hot_list.request_hot_list(10)

    # --- request_hot_list: success ---

    def test_request_success(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        api_resp = {
            "Code": 0,
            "Message": "ok",
            "Data": {
                "Total": 1,
                "Items": [
                    {
                        "Title": "Hot Topic",
                        "Url": "https://example.com",
                        "ThumbnailUrl": "https://img.example.com",
                        "Summary": "A hot topic summary",
                    }
                ],
            },
        }
        resp_body = json.dumps(api_resp).encode()
        with patch.object(
            hot_list, "urlopen", return_value=_fake_urlopen_bytes(resp_body)
        ):
            result = hot_list.request_hot_list(5)
        assert result["Code"] == 0
        assert result["Data"]["Total"] == 1

    # --- request_hot_list: HTTP error ---

    def test_request_http_error(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        err = _fake_urlopen_http_error(401, b'{"error":"unauthorized"}')
        with (
            patch.object(hot_list, "urlopen", side_effect=err),
            pytest.raises(SystemExit),
        ):
            hot_list.request_hot_list(5)

    # --- request_hot_list: timeout ---

    def test_request_timeout(self, monkeypatch):
        monkeypatch.setenv("ZHIHU_ACCESS_SECRET", "test-token")
        from urllib.error import URLError

        with (
            patch.object(hot_list, "urlopen", side_effect=URLError("timeout")),
            pytest.raises(SystemExit),
        ):
            hot_list.request_hot_list(5)
