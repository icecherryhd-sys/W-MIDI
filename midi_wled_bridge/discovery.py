"""Find WLED controllers on the local network."""

from __future__ import annotations

import ipaddress
import json
import socket
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class WledDevice:
    name: str
    ip: str


FetchJson = Callable[[str, float], dict[str, object] | None]


def parse_wled_info(ip: str, info: dict[str, object]) -> WledDevice | None:
    is_wled = any(key in info for key in ("ver", "vid", "leds", "brand"))
    if not is_wled:
        return None
    name = str(info.get("name") or info.get("brand") or "WLED").strip() or "WLED"
    return WledDevice(name=name, ip=ip)


def local_candidate_ips() -> list[str]:
    addresses = _local_ipv4_addresses()
    candidates: set[str] = set()
    for address in addresses:
        network = ipaddress.ip_network(f"{address}/24", strict=False)
        for host in network.hosts():
            ip = str(host)
            if ip != address:
                candidates.add(ip)
    return sorted(candidates, key=ipaddress.ip_address)


def discover_wled_devices(
    *,
    candidate_ips: Iterable[str] | None = None,
    fetch_json: FetchJson | None = None,
    timeout: float = 0.25,
    max_workers: int = 64,
) -> list[WledDevice]:
    ips = list(candidate_ips if candidate_ips is not None else local_candidate_ips())
    if not ips:
        return []
    fetch = fetch_json or fetch_wled_info
    workers = max(1, min(max_workers, len(ips)))
    devices: list[WledDevice] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_ip = {executor.submit(fetch, ip, timeout): ip for ip in ips}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                info = future.result()
            except Exception:
                continue
            if not info:
                continue
            device = parse_wled_info(ip, info)
            if device is not None:
                devices.append(device)

    return sorted(devices, key=lambda device: ipaddress.ip_address(device.ip))


def fetch_wled_info(ip: str, timeout: float) -> dict[str, object] | None:
    url = f"http://{ip}/json/info"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(65536)
    except (OSError, urllib.error.URLError, TimeoutError):
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _local_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()
    try:
        hostname = socket.gethostname()
        for result in socket.getaddrinfo(hostname, None, socket.AF_INET):
            address = result[4][0]
            parsed = ipaddress.ip_address(address)
            if not parsed.is_loopback and not parsed.is_link_local:
                addresses.add(address)
    except OSError:
        pass
    return sorted(addresses, key=ipaddress.ip_address)
