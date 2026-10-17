"""Register ONU"""

from data.customer_db import add_customer
from data.onu_types import DEFAULT_ONU_TYPE
from olt.find_onu_id import find_free_onu_id
from olt.parser import parse_uncfg
from olt.templates import register_commands
from olt.zte import olt_session


def get_unconfigured_onu() -> list:
    with olt_session() as s:
        return parse_uncfg(s.run("show gpon onu uncfg"))


def register_onu(pon, sn, name, package, vlan, mode, pppoe_user="", pppoe_pass="",
                 onu_type=DEFAULT_ONU_TYPE) -> int:
    """Register ONU on OLT, store customer in DB and return the ONU ID."""
    onu_id = find_free_onu_id(pon)
    with olt_session() as s:
        s.run_many(register_commands(pon, onu_id, onu_type, sn, name, package, vlan,
                                     mode, pppoe_user, pppoe_pass))
    add_customer({
        "name": name, "sn": sn, "pon": pon, "onu_id": str(onu_id), "vlan": vlan,
        "mode": mode, "package": package, "pppoe_user": pppoe_user,
        "pppoe_pass": pppoe_pass, "onu_type": onu_type,
    })
    return onu_id
