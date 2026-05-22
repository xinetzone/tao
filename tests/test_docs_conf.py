import importlib.metadata
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_conf_module():
    conf_path = Path(__file__).resolve().parents[1] / "docs" / "conf.py"
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
