"""MikroTik router list (edit or extend as needed)"""

import os

ROUTERS = {
    os.getenv("MT_ROUTER_NAME", "KWL"): {
        "host": os.getenv("MT_HOST", "192.168.88.1"),
        "port": int(os.getenv("MT_PORT", "8728")),
        "username": os.getenv("MT_USERNAME", "admin"),
        "password": os.getenv("MT_PASSWORD", ""),
    }
}
