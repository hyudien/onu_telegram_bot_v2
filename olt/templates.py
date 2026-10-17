"""ZTE command templates"""

import re

from data.packages import PACKAGES
from data.vlan_profiles import VLAN_PROFILES
from olt.zte import onu_iface


_SAFE_RE = re.compile(r"^[A-Za-z0-9._@\-]+$")
_SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9._@\- ]+$")


def safe(value, label: str = "Input", allow_space: bool = False) -> str:
    """Reject values that could inject extra CLI commands (whitespace, newlines, etc.)."""
    value = str(value)
    if not (_SAFE_NAME_RE if allow_space else _SAFE_RE).match(value):
        raise ValueError(f"{label} hanya boleh huruf, angka, titik, minus, underscore, dan @ (tanpa karakter lain)")
    return value


def _vlan_profile(vlan: str) -> str:
    return VLAN_PROFILES.get(str(vlan), f"VLAN{vlan}")


def register_commands(pon, onu_id, onu_type, sn, name, package, vlan, mode,
                      pppoe_user="", pppoe_pass="") -> list:
    iface = onu_iface(pon, onu_id)
    cmds = [
        "configure terminal",
        f"interface {pon}",
        f"onu {onu_id} type {safe(onu_type, 'Tipe ONU')} sn {safe(sn, 'SN')}",
        "exit",
        f"interface {iface}",
        f"name {safe(name, 'Nama', True)}",
        f"description {safe(name, 'Nama', True)}",
        f"tcont 1 name T1 profile {PACKAGES[package]}",
        "gemport 1 tcont 1",
        f"service-port 1 vport 1 user-vlan {vlan} vlan {vlan}",
        "exit",
        f"pon-onu-mng {iface}",
        f"service 1 gemport 1 vlan {vlan}",
    ]
    if "PPPOE" in mode:
        cmds.append(pppoe_command(vlan, pppoe_user, pppoe_pass))
    cmds += ["exit", "exit"]
    return cmds


def pppoe_command(vlan, user, secret) -> str:
    return (f"wan-ip 1 mode pppoe username {safe(user, 'PPPoE user')} password {safe(secret, 'PPPoE password')} "
            f"vlan-profile {_vlan_profile(vlan)} host 1")


def change_package_commands(pon, onu_id, package) -> list:
    return [
        "configure terminal",
        f"interface {onu_iface(pon, onu_id)}",
        f"tcont 1 name T1 profile {PACKAGES[package]}",
        "exit", "exit",
    ]


def change_pppoe_commands(pon, onu_id, vlan, user, secret) -> list:
    return [
        "configure terminal",
        f"pon-onu-mng {onu_iface(pon, onu_id)}",
        pppoe_command(vlan, user, secret),
        "exit", "exit",
    ]


def remote_access_commands(pon, onu_id) -> list:
    return [
        "configure terminal",
        f"pon-onu-mng {onu_iface(pon, onu_id)}",
        "security-mgmt 1 state enable mode forward protocol web",
        "exit", "exit",
    ]


def delete_commands(pon, onu_id) -> list:
    return ["configure terminal", f"interface {pon}", f"no onu {onu_id}", "exit", "exit"]


def reboot_commands(pon, onu_id) -> list:
    return ["configure terminal", f"pon-onu-mng {onu_iface(pon, onu_id)}", "reboot", "exit", "exit"]
