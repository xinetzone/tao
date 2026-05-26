#!/usr/bin/env python3
"""Zhida skill script (Python stdlib only)."""

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
from typing import Any, Dict, NoReturn, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://developer.zhihu.com"
REQUEST_TIMEOUT_SECONDS = 120


def print_usage() -> None:
    print(
        "Usage:\n"
        "  python3 zhida.py "
        '\'{"model":"zhida-thinking-1p5","messages":[{"role":"user","content":"如何理解 rave 文化"}]}\'\n\n'
        "Environment:\n"
        "  ZHIHU_ACCESS_SECRET      Bearer auth secret\n"
        "  ZHIHU_OPENAPI_BASE_URL   Optional, default https://developer.zhihu.com\n"
        "  ZHIHU_ZHIDA_URL          Optional full endpoint override\n"
    )


def die(message: str, *, body: Any | None = None) -> NoReturn:
    payload: Dict[str, Any] = {"error": message, "exit_code": 1}
    if body is not None:
        payload["body"] = body
    print(json.dumps(payload, ensure_ascii=False))
    raise SystemExit(1)


def parse_payload(raw: str) -> Dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        die("Invalid JSON payload")
    if not isinstance(payload, dict):
        die("Invalid JSON payload")
    return payload


def get_endpoint() -> str:
    explicit = os.getenv("ZHIHU_ZHIDA_URL", "").strip()
    if explicit:
        return explicit
    base_url = os.getenv("ZHIHU_OPENAPI_BASE_URL", DEFAULT_BASE_URL).strip()
    return f"{base_url.rstrip('/')}/v1/chat/completions"


def build_request_body(payload: Dict[str, Any]) -> Dict[str, Any]:
    model = str(payload.get("model", "")).strip().lower()
    if not model:
        die("model is required")

    body: Dict[str, Any] = {"model": model}

    if isinstance(payload.get("messages"), list) and payload["messages"]:
        body["messages"] = payload["messages"]
    else:
        die("messages is required")

    return body


def auth_headers() -> Dict[str, str]:
    secret = os.getenv("ZHIHU_ACCESS_SECRET", "").strip()
    if not secret:
        die("Set ZHIHU_ACCESS_SECRET first (Bearer auth only)")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {secret}",
        "X-Request-Timestamp": str(int(time.time())),
    }


def parse_http_error_body(body_text: str) -> Any:
    try:
        return json.loads(body_text)
    except json.JSONDecodeError:
        return body_text


def post_json(body: Dict[str, Any]) -> Tuple[int, Dict[str, str], Any]:
    request = Request(
        url=get_endpoint(),
        method="POST",
        headers=auth_headers(),
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", errors="replace")
    except HTTPError as err:
        body_text = err.read().decode("utf-8", errors="replace")
        die(f"HTTP {err.code}", body=parse_http_error_body(body_text))
    except (URLError, TimeoutError):
        die("HTTP request failed (timeout or network error)")


def normalize_non_stream(payload: Dict[str, Any]) -> Dict[str, Any]:
    choice = {}
    if isinstance(payload.get("choices"), list) and payload["choices"]:
        choice = payload["choices"][0] or {}
    message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    return {
        "code": 0,
        "id": payload.get("id", ""),
        "model": payload.get("model", ""),
        "content": message.get("content", ""),
        "reasoning_content": message.get("reasoning_content", ""),
        "finish_reason": choice.get("finish_reason", ""),
    }


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] in {"-h", "--help"}:
        print_usage()
        return
    if len(sys.argv) < 2:
        print_usage()
        raise SystemExit(1)

    payload = parse_payload(sys.argv[1])
    body = build_request_body(payload)
    _, _, raw_body = post_json(body)
    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError:
        die("Non-JSON response from API")
    result = normalize_non_stream(parsed)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
