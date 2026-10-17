"""MikroTik router configuration lookup"""

from data.mikrotik_routers import ROUTERS


def get_router_config(router: str) -> dict:
    if router not in ROUTERS:
        raise ValueError(f"Router {router} tidak terdaftar")
    return ROUTERS[router]
