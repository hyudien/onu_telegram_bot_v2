"""List unconfigured (newly discovered) ONUs"""

from olt.register_onu import get_unconfigured_onu

if __name__ == "__main__":
    for onu in get_unconfigured_onu():
        print(f"{onu['pon']}  {onu['sn']}")
