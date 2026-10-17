"""Sync PPPoE usernames from ONU configuration into the customer database"""

from data.customer_db import load_customers, save_customers
from olt.parser import parse_pppoe_user
from olt.zte import olt_session, onu_iface


def sync_pppoe() -> int:
    customers = load_customers()
    changed = 0
    with olt_session() as s:
        for c in customers:
            if c.get("pppoe_user") or not c.get("pon") or not c.get("onu_id"):
                continue
            user = parse_pppoe_user(s.run(f"show onu running config {onu_iface(c['pon'], c['onu_id'])}"))
            if user:
                c["pppoe_user"] = user
                changed += 1
    save_customers(customers)
    return changed


if __name__ == "__main__":
    print(f"{sync_pppoe()} PPPoE user diperbarui")
