"""Reboot ONU"""

from olt.templates import reboot_commands
from olt.zte import olt_session


def reboot_onu(pon, onu_id) -> None:
    with olt_session() as s:
        s.run_many(reboot_commands(pon, onu_id))
