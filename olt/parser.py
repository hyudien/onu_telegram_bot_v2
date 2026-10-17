"""Parse ZTE CLI output"""

import re

STATE_RE = re.compile(r"^\s*(\d+/\d+/\d+):(\d+)\s+(\S+)\s+(\S+)\s+(\S+)", re.M)
UNCFG_RE = re.compile(r"gpon-onu_(\d+/\d+/\d+):\d+\s+(\S+)\s+\S*", re.M)
BASEINFO_RE = re.compile(
    r"gpon-onu_(\d+/\d+/\d+):(\d+)\s+(\S+)\s+\S+\s+SN:(\S+)", re.M
)
PPPOE_USER_RE = re.compile(r"wan-ip\s+\d+\s+mode\s+pppoe\s+username\s+(\S+)", re.I)


def normalize_phase(phase: str) -> str:
    p = phase.lower()
    if p == "working":
        return "online"
    if p == "los":
        return "los"
    if p == "dyinggasp":
        return "dyinggasp"
    return "offline"


def parse_onu_state(text: str) -> list:
    """Parse `show gpon onu state <pon>`."""
    return [
        {"onu_id": int(m.group(2)), "admin": m.group(3), "phase": m.group(5),
         "status": normalize_phase(m.group(5))}
        for m in STATE_RE.finditer(text)
    ]


def parse_uncfg(text: str) -> list:
    """Parse `show gpon onu uncfg` into [{pon, sn}]."""
    return [
        {"pon": f"gpon-olt_{m.group(1)}", "sn": m.group(2)}
        for m in UNCFG_RE.finditer(text)
    ]


def parse_baseinfo(text: str) -> list:
    """Parse `show gpon onu baseinfo <pon>`."""
    return [
        {"onu_id": int(m.group(2)), "onu_type": m.group(3), "sn": m.group(4)}
        for m in BASEINFO_RE.finditer(text)
    ]


def parse_pppoe_user(text: str) -> str:
    m = PPPOE_USER_RE.search(text)
    return m.group(1) if m else ""
