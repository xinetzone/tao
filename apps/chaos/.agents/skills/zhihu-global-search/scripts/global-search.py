#!/usr/bin/env python3
"""Global search skill script (Python stdlib only)."""

from __future__ import annotations

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import json
import os
import sys
import time
from typing import Any, NoReturn
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://developer.zhihu.com"
REQUEST_TIMEOUT_SECONDS = 5


def print_usage() -> None:
    print(
        "Usage:\n"
        "  python3 global-search.py "
        '\'{"query":"如何理解 rave 文化","count":8,"filter":"host==\\"example.com\\"","search_db":"all"}\'\n\n'
        "Environment:\n"
        "  ZHIHU_ACCESS_SECRET      Bearer auth token\n"
        "  ZHIHU_OPENAPI_BASE_URL   Optional, default https://developer.zhihu.com\n"
        "  ZHIHU_GLOBAL_SEARCH_URL  Optional full endpoint override\n"
    )


def die(message: str, *, body: Any | None = None) -> NoReturn:
    payload: dict[str, Any] = {"error": message, "exit_code": 1}
    if body is not None:
        payload["body"] = body
    print(json.dumps(payload, ensure_ascii=False))
    raise SystemExit(1)


def parse_payload(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        die("Invalid JSON payload")
    if not isinstance(data, dict):
        die("Invalid JSON payload")
    return data


def parse_query(payload: dict[str, Any]) -> str:
    query = payload.get("query") or payload.get("Query") or ""
    if not isinstance(query, str) or not query.strip():
        die("query is required")
    query = query.strip()
    return query


def parse_count(payload: dict[str, Any]) -> int:
    raw = payload.get("count", payload.get("Count", 10))
    try:
        count = int(raw)
    except TypeError, ValueError:
        count = 10
    return max(1, min(20, count))


def parse_filter(payload: dict[str, Any]) -> str:
    raw = payload.get("filter", payload.get("Filter", ""))
    if raw is None:
        return ""
    if not isinstance(raw, str):
        die("filter must be a string")
    return raw.strip()


def parse_search_db(payload: dict[str, Any]) -> str:
    raw = payload.get("search_db", payload.get("SearchDB", ""))
    if raw is None:
        return ""
    if not isinstance(raw, str):
        die("search_db must be a string")
    value = raw.strip().lower()
    if value and value not in {"all", "realtime", "static"}:
        die("search_db must be one of all, realtime, static")
    return value


def get_endpoint() -> str:
    explicit = os.getenv("ZHIHU_GLOBAL_SEARCH_URL", "").strip()
    if explicit:
        return explicit
    base_url = os.getenv("ZHIHU_OPENAPI_BASE_URL", DEFAULT_BASE_URL).strip()
    return f"{base_url.rstrip('/')}/api/v1/content/global_search"


def request_global_search(
    query: str, count: int, filter_expr: str, search_db: str
) -> dict[str, Any]:
    secret = os.getenv("ZHIHU_ACCESS_SECRET", "").strip()
    if not secret:
        die("Set ZHIHU_ACCESS_SECRET first (Bearer auth only)")

    params_dict = {"Query": query, "Count": str(count)}
    if filter_expr:
        params_dict["Filter"] = filter_expr
    if search_db:
        params_dict["SearchDB"] = search_db
    params = urlencode(params_dict)
    url = f"{get_endpoint()}?{params}"
    req = Request(
        url=url,
        method="GET",
        headers={
            "Authorization": f"Bearer {secret}",
            "X-Request-Timestamp": str(int(time.time())),
        },
    )

    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
    except HTTPError as err:
        body_text = err.read().decode("utf-8", errors="replace")
        die(f"HTTP {err.code}", body=body_text)
    except URLError, TimeoutError:
        die("HTTP request failed (timeout or network error)")

    try:
        return json.loads(body_text)
    except json.JSONDecodeError:
        die("Non-JSON response from API")


def normalize_items(api_resp: dict[str, Any]) -> dict[str, Any]:
    data = api_resp.get("Data") if isinstance(api_resp.get("Data"), dict) else {}
    items = data.get("Items") if isinstance(data.get("Items"), list) else []
    normalized_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized_items.append(
            {
                "title": item.get("Title", ""),
                "url": item.get("Url", ""),
                "author_name": item.get("AuthorName", ""),
                "summary": item.get("ContentText", ""),
                "edit_time": item.get("EditTime", 0),
            }
        )

    return {
        "code": api_resp.get("Code", -1),
        "message": api_resp.get("Message", ""),
        "item_count": len(normalized_items),
        "items": normalized_items,
    }


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] in {"-h", "--help"}:
        print_usage()
        return

    if len(sys.argv) < 2:
        print_usage()
        raise SystemExit(1)

    payload = parse_payload(sys.argv[1])
    query = parse_query(payload)
    count = parse_count(payload)
    filter_expr = parse_filter(payload)
    search_db = parse_search_db(payload)

    api_resp = request_global_search(query, count, filter_expr, search_db)
    result = normalize_items(api_resp)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
