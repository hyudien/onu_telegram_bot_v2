"""Enable remote (web) access on ONU"""

from olt.templates import remote_access_commands
from olt.zte import olt_session


def enable_remote(pon, onu_id) -> None:
    with olt_session() as s:
        s.run_many(remote_access_commands(pon, onu_id))
