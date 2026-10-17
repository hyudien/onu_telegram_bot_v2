"""Change ONU PPPoE credentials"""

from data.customer_db import update_customer
from olt.templates import change_pppoe_commands
from olt.zte import olt_session


def change_pppoe(pon, onu_id, vlan, user, secret) -> None:
    with olt_session() as s:
        s.run_many(change_pppoe_commands(pon, onu_id, vlan, user, secret))
    update_customer(pon, onu_id, pppoe_user=user, pppoe_pass=secret)
