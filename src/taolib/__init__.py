from importlib.metadata import version, PackageNotFoundError


def get_version(pkg_name: str) -> str:
    try:
        return version(pkg_name)
    except PackageNotFoundError:
        return "0.0.0"
