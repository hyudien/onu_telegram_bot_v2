"""Get ONU information"""

from olt.zte import olt_session, onu_iface


def get_onu_info(pon: str, onu_id) -> str:
    with olt_session() as s:
        return s.run(f"show gpon onu detail-info {onu_iface(pon, onu_id)}")
