"""Save OLT configuration"""

from olt.zte import olt_session


def save_config() -> str:
    with olt_session() as s:
        return s.run("write", timeout=60)
