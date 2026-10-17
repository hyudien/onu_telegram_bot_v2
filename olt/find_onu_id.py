"""Find free ONU ID on a PON"""

from olt.parser import parse_onu_state
from olt.zte import olt_session

MAX_ONU = 128


def find_free_onu_id(pon: str) -> int:
    with olt_session() as s:
        used = {o["onu_id"] for o in parse_onu_state(s.run(f"show gpon onu state {pon}"))}
    for i in range(1, MAX_ONU + 1):
        if i not in used:
            return i
    raise ValueError(f"Tidak ada ONU ID kosong di {pon}")
