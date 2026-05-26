#!/usr/bin/env python3
"""Hot list skill script (Python stdlib only)."""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, NoReturn
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://developer.zhihu.com"
REQUEST_TIMEOUT_SECONDS = 5


def print_usage() -> None:
    print(
        "Usage:\n"
        '  python3 hot-list.py \'{"limit":10}\'\n\n'
        "Environment:\n"
        "  ZHIHU_ACCESS_SECRET   Bearer auth secret\n"
        "  ZHIHU_OPENAPI_BASE_URL Optional, default https://developer.zhihu.com\n"
        "  ZHIHU_HOT_LIST_URL    Optional full endpoint override\n"
    )


def die(message: str, *, body: Any | None = None) -> NoReturn:
    payload: Dict[str, Any] = {"error": message, "exit_code": 1}
    if body is not None:
        payload["body"] = body
    print(json.dumps(payload, ensure_ascii=False))
    raise SystemExit(1)


def parse_payload(raw: str) -> Dict[str, Any]:
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        die("Invalid JSON payload")
    if not isinstance(payload, dict):
        die("Invalid JSON payload")
    return payload


def parse_limit(payload: Dict[str, Any]) -> int:
    raw = payload.get("limit", payload.get("Limit", 30))
    try:
        limit = int(raw)
    except (TypeError, ValueError):
        limit = 30
    return max(1, min(30, limit))


def get_endpoint() -> str:
    explicit = os.getenv("ZHIHU_HOT_LIST_URL", "").strip()
    if explicit:
        return explicit
    base_url = os.getenv("ZHIHU_OPENAPI_BASE_URL", DEFAULT_BASE_URL).strip()
    return f"{base_url.rstrip('/')}/api/v1/content/hot_list"


def request_hot_list(limit: int) -> Dict[str, Any]:
    secret = os.getenv("ZHIHU_ACCESS_SECRET", "").strip()
    if not secret:
        die("Set ZHIHU_ACCESS_SECRET first (Bearer auth only)")
    query = urlencode({"Limit": str(limit)})
    request = Request(
        url=f"{get_endpoint()}?{query}",
        method="GET",
        headers={
            "Authorization": f"Bearer {secret}",
            "X-Request-Timestamp": str(int(time.time())),
        },
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
    except HTTPError as err:
        body_text = err.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(body_text)
        except json.JSONDecodeError:
            body = body_text
        die(f"HTTP {err.code}", body=body)
    except (URLError, TimeoutError):
        die("HTTP request failed (timeout or network error)")

    try:
        return json.loads(body_text)
    except json.JSONDecodeError:
        die("Non-JSON response from API")


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] in {"-h", "--help"}:
        print_usage()
        return
    payload = parse_payload(sys.argv[1] if len(sys.argv) >= 2 else "{}")
    response = request_hot_list(parse_limit(payload))
    data = response.get("Data") if isinstance(response.get("Data"), dict) else {}
    items = data.get("Items") if isinstance(data.get("Items"), list) else []
    normalized_items = [
        {
            "title": item.get("Title", ""),
            "url": item.get("Url", ""),
            "thumbnail_url": item.get("ThumbnailUrl", ""),
            "summary": item.get("Summary", ""),
        }
        for item in items
        if isinstance(item, dict)
    ]
    result = {
        "code": response.get("Code", -1),
        "message": response.get("Message", ""),
        "total": data.get("Total", len(items)),
        "item_count": len(normalized_items),
        "items": normalized_items,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
