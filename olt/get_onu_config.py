"""Get ONU configuration"""

from olt.zte import olt_session, onu_iface


def get_onu_config(pon: str, onu_id) -> str:
    with olt_session() as s:
        return s.run(f"show onu running config {onu_iface(pon, onu_id)}")
