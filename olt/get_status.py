"""OLT status monitoring"""

from data.customer_db import get_customer
from data.pons import PON_NAMES
from olt.parser import parse_onu_state
from olt.zte import olt_session


def get_pon_info(pon: str) -> list:
    """Return parsed ONU states for a PON."""
    with olt_session() as s:
        return parse_onu_state(s.run(f"show gpon onu state {pon}"))


def get_pon_summary_live(pon_data: list) -> dict:
    count = {"online": 0, "los": 0, "dyinggasp": 0, "offline": 0}
    for o in pon_data:
        count[o["status"]] += 1
    return {
        "online": count["online"],
        "offline": len(pon_data) - count["online"],
        "los": count["los"],
        "dyinggasp": count["dyinggasp"],
        "total": len(pon_data),
    }


def get_pon_problem_customers_live(pon_data: list, pon: str) -> list:
    problems = []
    for o in pon_data:
        if o["status"] == "online":
            continue
        cust = get_customer(pon, o["onu_id"])
        problems.append({
            "onu_id": o["onu_id"],
            "name": cust.get("name", "-"),
            "status": o["status"],
        })
    return problems


def get_summary() -> dict:
    total = {"online": 0, "offline": 0, "los": 0, "dyinggasp": 0, "total": 0}
    with olt_session() as s:
        for pon in PON_NAMES:
            summary = get_pon_summary_live(parse_onu_state(s.run(f"show gpon onu state {pon}")))
            for k in total:
                total[k] += summary[k]
    return total
