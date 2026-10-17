"""Change ONU package"""

from data.customer_db import update_customer
from olt.templates import change_package_commands
from olt.zte import olt_session


def change_package(pon, onu_id, package) -> None:
    with olt_session() as s:
        s.run_many(change_package_commands(pon, onu_id, package))
    update_customer(pon, onu_id, package=package)
