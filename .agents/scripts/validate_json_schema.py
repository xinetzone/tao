"""通用 JSON Schema 验证 CLI 工具.

用法::

    python validate_json_schema.py <json_file> <schema_file>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def validate_with_jsonschema(data: dict, schema: dict) -> str | None:
    """使用 jsonschema 库验证，返回 None 表示通过，否则返回错误信息。"""
    try:
        import jsonschema
    except ImportError:
        return "__FALLBACK__"
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        return str(e.message)
    return None


def validate_basic(data: dict, schema: dict) -> str | None:
    """降级验证：检查 required 字段存在性和基本类型。"""
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    for field in required:
        if field not in data:
            return f"Missing required field: {field}"
        prop_schema = properties.get(field, {})
        expected_type = prop_schema.get("type")
        if expected_type == "integer" and not isinstance(data[field], int):
            return f"Field '{field}' expected integer, got {type(data[field]).__name__}"
        if expected_type == "array" and not isinstance(data[field], list):
            return f"Field '{field}' expected array, got {type(data[field]).__name__}"
        if expected_type == "object" and not isinstance(data[field], dict):
            return f"Field '{field}' expected object, got {type(data[field]).__name__}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="通用 JSON Schema 验证工具")
    parser.add_argument("json_file", help="待验证的 JSON 文件路径")
    parser.add_argument("schema_file", help="JSON Schema 文件路径")
    args = parser.parse_args()

    json_path = Path(args.json_file)
    schema_path = Path(args.schema_file)

    if not json_path.exists():
        print(f"[ERROR] File not found: {json_path}")
        return 2
    if not schema_path.exists():
        print(f"[ERROR] File not found: {schema_path}")
        return 2

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError, ValueError:
        print(f"[ERROR] Invalid JSON: {json_path}")
        return 2

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError, ValueError:
        print(f"[ERROR] Invalid JSON: {schema_path}")
        return 2

    result = validate_with_jsonschema(data, schema)
    if result == "__FALLBACK__":
        print("[WARN] jsonschema unavailable, using basic assertions")
        result = validate_basic(data, schema)

    if result is None:
        print(f"[PASS] {json_path} conforms to {schema_path}")
        return 0
    else:
        print(f"[FAIL] Validation error: {result}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
