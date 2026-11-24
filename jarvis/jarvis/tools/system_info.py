"""System status: CPU, memory, disk, battery, uptime, time and network.

Works on Windows and Linux (anything psutil supports). psutil is imported
lazily so the time tool still works without it.
"""

from __future__ import annotations

import os
import socket
import time
import urllib.request
from datetime import datetime

from . import tool


def _psutil():
    try:
        import psutil  # noqa: PLC0415
        return psutil
    except ImportError:
        return None


def _duration(seconds: float) -> str:
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes or not parts:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    return ", ".join(parts)


def _system_drive() -> str:
    if os.name == "nt":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"


@tool("system_status", "Report how the computer is doing: CPU and memory use, free disk space on "
      "the system drive, battery level and charging state, and uptime.")
def system_status() -> str:
    psutil = _psutil()
    if psutil is None:
        return "Error: the psutil package is not installed."
    parts = [f"CPU at {psutil.cpu_percent(interval=0.5):.0f} percent"]
    mem = psutil.virtual_memory()
    parts.append(f"memory at {mem.percent:.0f} percent of {mem.total / 2**30:.0f} gigabytes")
    drive = _system_drive()
    try:
        du = psutil.disk_usage(drive)
        label = "C drive" if drive.upper().startswith("C:") else ("the system drive" if os.name == "nt" else "the main disk")
        parts.append(f"{du.free / 2**30:.0f} gigabytes free on {label}")
    except OSError:
        pass
    try:
        bat = psutil.sensors_battery()
    except (AttributeError, NotImplementedError, OSError):
        bat = None
    if bat is not None:
        state = "charging" if bat.power_plugged else "on battery"
        parts.append(f"battery {bat.percent:.0f} percent and {state}")
    else:
        parts.append("no battery detected")
    parts.append(f"up for {_duration(time.time() - psutil.boot_time())}")
    return ", ".join(parts[:-1]) + ", and " + parts[-1] + "."


@tool("current_time_date", "Tell the current local time, day and date.")
def current_time_date() -> str:
    now = datetime.now()
    hour = now.strftime("%I").lstrip("0") or "12"
    return f"It's {hour}:{now.strftime('%M %p')} on {now.strftime('%A, %B')} {now.day}, {now.year}."


def _local_ip() -> str | None:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # UDP connect sends no packets; it only picks the outgoing interface.
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        try:
            ip = socket.gethostbyname(socket.gethostname())
            return None if ip.startswith("127.") else ip
        except OSError:
            return None
    finally:
        s.close()


def _online() -> bool:
    for host in (("1.1.1.1", 53), ("8.8.8.8", 53)):
        try:
            with socket.create_connection(host, timeout=2):
                return True
        except OSError:
            continue
    try:  # Behind a proxy / firewall that blocks raw DNS ports.
        with urllib.request.urlopen("http://www.msftconnecttest.com/connecttest.txt", timeout=3) as r:
            return r.status == 200
    except Exception:  # noqa: BLE001
        return False


@tool("ip_and_network", "Tell the computer's local IP address, Wi-Fi/network connection and "
      "whether it is online.")
def ip_and_network() -> str:
    ip = _local_ip()
    out = [f"Your local IP is {ip}" if ip else "I couldn't find a local IP address"]
    psutil = _psutil()
    if psutil is not None:
        try:
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            up = [n for n, st in stats.items() if st.isup and n in addrs
                  and not n.lower().startswith(("lo", "loopback"))
                  and any(a.family == socket.AF_INET and a.address == ip for a in addrs[n])]
            if up:
                out.append(f"on {up[0]}")
        except Exception:  # noqa: BLE001
            pass
    out.append("and you're online." if _online() else "and you appear to be offline.")
    return " ".join(out)
