"""MikroTik connection handler"""

from contextlib import contextmanager

import routeros_api

from mikrotik.config import get_router_config


@contextmanager
def connect(router: str):
    """Yield a RouterOS API object and always close the connection."""
    cfg = get_router_config(router)
    pool = routeros_api.RouterOsApiPool(
        cfg["host"],
        username=cfg["username"],
        password=cfg["password"],
        port=cfg.get("port", 8728),
        plaintext_login=True,
    )
    try:
        yield pool.get_api()
    finally:
        pool.disconnect()
