"""Delete ONU"""

from data.customer_db import delete_customer
from olt.templates import delete_commands
from olt.zte import olt_session


def delete_onu(pon, onu_id) -> None:
    with olt_session() as s:
        s.run_many(delete_commands(pon, onu_id))
    delete_customer(pon, onu_id)
