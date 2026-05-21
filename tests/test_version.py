import taolib


def test_version_returns_str():
    assert isinstance(taolib.version(), str)
    assert taolib.version()


def test_dunder_version_is_deprecated():
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        v = taolib.__version__

    assert any(item.category is DeprecationWarning for item in w)
    assert v == taolib.version()
