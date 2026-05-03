"""Mocked Cisco network topology and telemetry tools."""
from typing import Any

_TOPOLOGY: dict[str, Any] = {
    "devices": [
        {
            "device_id": "sj-catalyst-01",
            "hostname": "sj-catalyst-01.corp.local",
            "model": "Catalyst 9300",
            "site": "San Jose",
            "role": "access",
            "interfaces": ["GigE0/1", "GigE0/2", "GigE0/3", "GigE0/24", "TenGigE1/1"],
            "uplinks": ["sj-core-01"],
            "vlans": [100, 200, 300],
        },
        {
            "device_id": "sj-core-01",
            "hostname": "sj-core-01.corp.local",
            "model": "Catalyst 9500",
            "site": "San Jose",
            "role": "core",
            "interfaces": ["TenGigE1/1", "TenGigE1/2", "FortyGigE1/1"],
            "uplinks": ["sj-wan-01"],
        },
    ],
    "links": [
        {"from": "sj-catalyst-01:TenGigE1/1", "to": "sj-core-01:TenGigE1/1", "bandwidth_gbps": 10},
    ],
}

_TELEMETRY: dict[str, Any] = {
    "sj-catalyst-01": {
        "GigE0/1": {
            "in_errors": 12, "out_errors": 2847, "drops": 1923,
            "utilization_pct": 94.2, "speed_mbps": 1000, "status": "up",
            "last_cleared": "2024-02-14T00:00:00Z",
        },
        "GigE0/2": {
            "in_errors": 0, "out_errors": 3, "drops": 1,
            "utilization_pct": 12.4, "speed_mbps": 1000, "status": "up",
        },
        "GigE0/3": {
            "in_errors": 0, "out_errors": 1, "drops": 0,
            "utilization_pct": 8.1, "speed_mbps": 1000, "status": "up",
        },
        "TenGigE1/1": {
            "in_errors": 0, "out_errors": 0, "drops": 0,
            "utilization_pct": 44.8, "speed_mbps": 10000, "status": "up",
        },
    },
}


def get_network_topology(site: str = "", device_id: str = "") -> dict[str, Any]:
    devices = list(_TOPOLOGY["devices"])
    if site:
        devices = [d for d in devices if d["site"].lower() == site.lower()]
    if device_id:
        devices = [d for d in devices if d["device_id"] == device_id]
    return {"devices": devices, "links": _TOPOLOGY["links"], "total_devices": len(devices)}


def get_telemetry_metrics(
    device_id: str,
    interface: str = "",
    time_window: str = "last 5 minutes",
) -> dict[str, Any]:
    device = _TELEMETRY.get(device_id, {})
    if interface:
        metrics = device.get(interface, {})
        anomaly = metrics.get("out_errors", 0) > 500 or metrics.get("utilization_pct", 0) > 90
        return {
            "device_id": device_id,
            "interface": interface,
            "time_window": time_window,
            "metrics": metrics,
            "anomaly": anomaly,
        }
    return {"device_id": device_id, "time_window": time_window, "interfaces": device}
