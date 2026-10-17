"""Sync OLT ONU data into the local customer database"""

from data.customer_db import load_customers, save_customers
from data.pons import PON_NAMES
from olt.parser import parse_baseinfo
from olt.zte import olt_session


def sync_olt_db() -> dict:
    """Add ONUs found on the OLT that are missing from the DB and refresh SN/type."""
    customers = load_customers()
    index = {(c.get("pon"), str(c.get("onu_id"))): c for c in customers}
    added = updated = 0

    with olt_session() as s:
        for pon in PON_NAMES:
            for onu in parse_baseinfo(s.run(f"show gpon onu baseinfo {pon}")):
                key = (pon, str(onu["onu_id"]))
                cust = index.get(key)
                if cust is None:
                    customers.append({
                        "name": f"ONU {pon.split('_')[-1]}:{onu['onu_id']}",
                        "sn": onu["sn"], "pon": pon, "onu_id": str(onu["onu_id"]),
                        "onu_type": onu["onu_type"],
                    })
                    added += 1
                elif cust.get("sn") != onu["sn"] or cust.get("onu_type") != onu["onu_type"]:
                    cust["sn"], cust["onu_type"] = onu["sn"], onu["onu_type"]
                    updated += 1

    save_customers(customers)
    return {"added": added, "updated": updated, "total": len(customers)}


if __name__ == "__main__":
    print(sync_olt_db())
