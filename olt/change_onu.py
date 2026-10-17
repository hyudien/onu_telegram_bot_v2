"""Replace ONU device (new serial number, same ONU ID, same config)"""

from data.customer_db import update_customer
from olt.templates import delete_commands, register_commands
from olt.zte import olt_session


def change_onu(customer: dict, new_sn: str) -> None:
    pon, onu_id = customer["pon"], customer["onu_id"]
    onu_type = customer.get("onu_type", "ALL-ONT")
    with olt_session() as s:
        s.run_many(delete_commands(pon, onu_id))
        s.run_many(register_commands(
            pon, onu_id, onu_type, new_sn, customer.get("name", "-"),
            customer["package"], customer["vlan"], customer["mode"],
            customer.get("pppoe_user", ""), customer.get("pppoe_pass", ""),
        ))
    update_customer(pon, onu_id, sn=new_sn)
