"""MikroTik PPPoE user queries"""

from mikrotik.api import resource, is_true


def get_all_users(router: str) -> list:
    with resource(router, "/ppp/secret") as secrets:
        return secrets.get()


def get_online_users(router: str) -> list:
    with resource(router, "/ppp/active") as active:
        return sorted(a["name"] for a in active.get() if "name" in a)


def get_offline_users(router: str) -> list:
    online = set(get_online_users(router))
    return sorted(u["name"] for u in get_all_users(router) if u["name"] not in online)


def get_user(router: str, username: str):
    """Return user info dict or None."""
    with resource(router, "/ppp/secret") as secrets:
        found = secrets.get(name=username)
    if not found:
        return None
    u = found[0]
    return {
        "name": u["name"],
        "profile": u.get("profile", "-"),
        "comment": u.get("comment", "-"),
        "disabled": is_true(u.get("disabled", "false")),
    }
