"""Customer database (JSON file)"""

import json
import os
from datetime import datetime

CUSTOMER_FILE = os.path.join(os.path.dirname(__file__), "customers.json")


def load_customers() -> list:
    if not os.path.exists(CUSTOMER_FILE):
        return []
    try:
        with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return []


def save_customers(customers: list) -> None:
    tmp = CUSTOMER_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CUSTOMER_FILE)


def find_customers(keyword: str) -> list:
    """Search by name, SN or PPPoE user (case-insensitive substring)."""
    keyword = keyword.strip().lower()
    if not keyword:
        return []
    return [
        c for c in load_customers()
        if any(keyword in str(c.get(k, "")).lower() for k in ("name", "sn", "pppoe_user"))
    ]


def get_customer(pon: str, onu_id) -> dict:
    for c in load_customers():
        if c.get("pon") == pon and str(c.get("onu_id")) == str(onu_id):
            return c
    return {}


def add_customer(customer: dict) -> None:
    customers = load_customers()
    customer.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    customers.append(customer)
    save_customers(customers)


def update_customer(pon: str, onu_id, **fields) -> bool:
    customers = load_customers()
    for c in customers:
        if c.get("pon") == pon and str(c.get("onu_id")) == str(onu_id):
            c.update(fields)
            save_customers(customers)
            return True
    return False


def delete_customer(pon: str, onu_id) -> None:
    customers = [
        c for c in load_customers()
        if not (c.get("pon") == pon and str(c.get("onu_id")) == str(onu_id))
    ]
    save_customers(customers)
