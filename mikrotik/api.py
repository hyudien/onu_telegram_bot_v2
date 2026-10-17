"""MikroTik API wrapper"""

from contextlib import contextmanager

from mikrotik.koneksi import connect


@contextmanager
def resource(router: str, path: str):
    """Yield a RouterOS resource (e.g. /ppp/secret)."""
    with connect(router) as api:
        yield api.get_resource(path)


def is_true(value) -> bool:
    return str(value).lower() in ("true", "yes")
