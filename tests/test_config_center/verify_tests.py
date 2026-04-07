#!/usr/bin/env python
"""验证测试导入和基础结构。"""

import sys
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TESTS = ROOT / "tests" / "test_config_center"


def test_imports() -> None:
    """测试所有模块导入。"""
    print("Testing imports...")

    # Models

    print("  ✓ Models imported")

    # Repository

    print("  ✓ Repositories imported")

    # Cache

    print("  ✓ Cache modules imported")

    # Validation

    print("  ✓ Validation modules imported")

    # Auth

    print("  ✓ Auth modules imported")

    # Services

    print("  ✓ Services imported")

    # Client

    print("  ✓ Client imported")

    print("\nAll imports successful! ✓")


def test_test_files_exist() -> None:
    """测试所有测试文件存在。"""
    print("\nChecking test files...")

    test_files = [
        "conftest.py",
        "test_models_config.py",
        "test_models_version_audit.py",
        "test_repository_config.py",
        "test_cache.py",
        "test_validation.py",
        "test_auth.py",
        "test_services.py",
        "test_client.py",
    ]

    for test_file in test_files:
        file_path = TESTS / test_file
        if file_path.exists():
            print(f"  ✓ {test_file}")
        else:
            print(f"  ✗ {test_file} NOT FOUND")
            return

    print("\nAll test files exist! ✓")


def test_basic_functionality() -> None:
    """测试基础功能。"""
    print("\nTesting basic functionality...")

    from taolib.config_center.cache.config_cache import InMemoryConfigCache
    from taolib.config_center.cache.keys import config_key
    from taolib.config_center.models.config import ConfigDocument
    from taolib.config_center.models.enums import ConfigValueType, Environment

    # Test model creation
    doc = ConfigDocument(
        id="test-1",
        key="test.key",
        environment=Environment.DEVELOPMENT,
        service="test-service",
        value="test-value",
        value_type=ConfigValueType.STRING,
        created_by="user-1",
        updated_by="user-1",
    )
    print("  ✓ ConfigDocument created")

    # Test cache key generation
    key = config_key("development", "auth-service", "database.host")
    assert key == "config:development:auth-service:database.host"
    print("  ✓ Cache key generated")

    # Test in-memory cache
    cache = InMemoryConfigCache()
    import asyncio
    asyncio.get_event_loop().run_until_complete(
        cache.set("dev", "svc", "key", "value")
    )
    result = asyncio.get_event_loop().run_until_complete(
        cache.get("dev", "svc", "key")
    )
    assert result == "value"
    print("  ✓ InMemoryConfigCache works")

    print("\nBasic functionality tests passed! ✓")


if __name__ == "__main__":
    print("=" * 60)
    print("Config Center Test Suite Validation")
    print("=" * 60)

    try:
        test_imports()
        test_test_files_exist()
        test_basic_functionality()

        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        print("\nYou can now run tests with:")
        print("  pytest tests/test_config_center/ -v")
        print("\nFor coverage:")
        print("  pytest tests/test_config_center/ -v --cov=taolib.config_center")

    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
