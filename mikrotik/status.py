"""MikroTik status monitoring"""

from mikrotik.api import resource
from mikrotik.users import get_all_users, get_online_users


def get_status(router: str) -> dict:
    total = len(get_all_users(router))
    online = len(get_online_users(router))
    with resource(router, "/system/resource") as res:
        info = res.get()[0]
    used = (int(info.get("total-memory", 0)) - int(info.get("free-memory", 0))) // (1024 * 1024)
    return {
        "total": total,
        "online": online,
        "offline": max(total - online, 0),
        "cpu": info.get("cpu-load", "0"),
        "memory": used,
        "uptime": info.get("uptime", "-"),
    }
