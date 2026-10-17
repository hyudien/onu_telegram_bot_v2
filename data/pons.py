"""PON list (key = OLT interface, value = display name)"""

PON_NAMES = {f"gpon-olt_1/1/{i}": f"PON 1/1/{i}" for i in range(1, 9)}
