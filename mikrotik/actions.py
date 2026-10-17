"""MikroTik PPPoE user CRUD operations"""

from mikrotik.api import resource


def _secret_id(secrets, username: str) -> str:
    found = secrets.get(name=username)
    if not found:
        raise ValueError(f"User {username} tidak ditemukan")
    return found[0]["id"]


def find_users(router: str, keyword: str) -> list:
    """Return usernames matching keyword (exact match first)."""
    keyword = keyword.strip().lower()
    with resource(router, "/ppp/secret") as secrets:
        names = [u["name"] for u in secrets.get()]
    if keyword in [n.lower() for n in names]:
        return [n for n in names if n.lower() == keyword]
    return sorted(n for n in names if keyword in n.lower())


def add_user(router: str, username: str, password: str, profile: str, comment: str = "") -> None:
    with resource(router, "/ppp/secret") as secrets:
        if secrets.get(name=username):
            raise ValueError(f"User {username} sudah ada")
        params = dict(name=username, password=password, profile=profile, service="pppoe")
        if comment:
            params["comment"] = comment
        secrets.add(**params)


def delete_user(router: str, username: str) -> None:
    with resource(router, "/ppp/secret") as secrets:
        secrets.remove(id=_secret_id(secrets, username))


def _set(router: str, username: str, **fields) -> None:
    with resource(router, "/ppp/secret") as secrets:
        secrets.set(id=_secret_id(secrets, username), **fields)


def set_password(router: str, username: str, password: str) -> None:
    _set(router, username, password=password)


def set_profile(router: str, username: str, profile: str) -> None:
    _set(router, username, profile=profile)


def set_comment(router: str, username: str, comment: str) -> None:
    _set(router, username, comment=comment)


def enable_user(router: str, username: str) -> None:
    _set(router, username, disabled="no")


def disable_user(router: str, username: str) -> None:
    _set(router, username, disabled="yes")
