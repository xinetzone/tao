import importlib.metadata
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


def _get_docs_conf() -> Path | None:
    """Search upward from the test file to locate docs/conf.py.

    Works in both monorepo (tests/ nested under apps/chaos/) and
    container (tests/ directly under /app/) layouts.
    Returns None if not found (e.g., container without docs/).
    """
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / "docs" / "conf.py"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


DOCS_CONF = _get_docs_conf()


def _load_conf_module():
    if DOCS_CONF is None:
        pytest.skip(
            "docs/conf.py not found (likely running in container without docs/)"
        )
    conf_path = DOCS_CONF
    spec = spec_from_file_location("docs_conf", conf_path)
    assert spec is not None
    assert spec.loader is not None

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_docs_conf_release_uses_distribution_version(monkeypatch):
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "1.2.3")

    module = _load_conf_module()

    assert module.release == "1.2.3"
    assert module.version == module.release


def test_docs_conf_release_falls_back_when_metadata_is_missing(monkeypatch):
    def _raise_package_not_found(_name: str) -> str:
        raise importlib.metadata.PackageNotFoundError("taolib")

    monkeypatch.setattr(importlib.metadata, "version", _raise_package_not_found)

    module = _load_conf_module()

    assert module.release == "0+unknown"
    assert module.version == module.release
