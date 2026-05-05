"""Mocked CI network topology and telemetry tools.

Maps to Cisco Catalyst Center MCP server (separate from Splunk MCP).
"""
import time
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
            "downstream_devices": ["sj-catalyst-01"],
            "blast_radius": "All San Jose access layer",
        },
        {
            "device_id": "sj-edge-01",
            "hostname": "sj-edge-01.corp.local",
            "model": "ASR 1001-X",
            "site": "San Jose",
            "role": "wan_edge",
            "interfaces": ["GigE0/0", "GigE0/1", "TenGigE0/0/0"],
            "uplinks": ["upstream-isp-01"],
            "bgp_peers": [{"peer_ip": "203.0.113.1", "peer_as": 64500, "peer_name": "upstream-isp-01"}],
            "downstream_devices": ["sj-core-01"],
        },
    ],
    "links": [
        {"from": "sj-catalyst-01:TenGigE1/1", "to": "sj-core-01:TenGigE1/1", "bandwidth_gbps": 10},
        {"from": "sj-core-01:FortyGigE1/1", "to": "sj-edge-01:TenGigE0/0/0", "bandwidth_gbps": 40},
        {"from": "sj-edge-01:GigE0/0", "to": "upstream-isp-01:GigE0/0", "bandwidth_gbps": 1,
         "link_type": "wan_mpls"},
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
        "TenGigE1/1": {
            "in_errors": 0, "out_errors": 0, "drops": 0,
            "utilization_pct": 44.8, "speed_mbps": 10000, "status": "up",
        },
    },
    "sj-edge-01": {
        "GigE0/0": {
            "in_errors": 0, "out_errors": 0, "drops": 0,
            "utilization_pct": 38.2, "speed_mbps": 1000, "status": "up",
            "mtu": 1500,
            "bgp_session_state": "Idle",
            "bgp_down_reason": "keepalive_timeout",
            "bgp_flap_count": 23,
            "is_security_threat": False,
            "note": "BGP hold timer expiry — keepalives dropped due to MTU mismatch (local=1500, ISP requires=1480). No security indicators. Fix: ip mtu 1480.",
        },
        "GigE0/1": {
            "in_errors": 0, "out_errors": 0, "drops": 0,
            "utilization_pct": 8.1, "speed_mbps": 1000, "status": "up",
        },
        "TenGigE0/0/0": {
            "in_errors": 0, "out_errors": 0, "drops": 0,
            "utilization_pct": 44.8, "speed_mbps": 10000, "status": "up",
        },
    },
    "sj-core-01": {
        "_device_metrics": {
            "cpu_pct": 94.1, "memory_pct": 89.3,
            "cpu_spike_at": "2024-02-15T14:54:00Z",
            "bgp_status": "degraded", "stp_status": "degraded",
            "anomaly": True,
            "note": "CPU 94% — BGP and STP convergence degraded. All downstream devices affected.",
        },
        "TenGigE1/1": {
            "in_errors": 0, "out_errors": 0, "drops": 1847,
            "utilization_pct": 67.2, "speed_mbps": 10000, "status": "up",
        },
        "TenGigE1/2": {
            "in_errors": 0, "out_errors": 0, "drops": 923,
            "utilization_pct": 54.1, "speed_mbps": 10000, "status": "up",
        },
        "FortyGigE1/1": {
            "in_errors": 0, "out_errors": 0, "drops": 0,
            "utilization_pct": 41.3, "speed_mbps": 40000, "status": "up",
        },
    },
}


def get_network_topology(site: str = "", device_id: str = "") -> dict[str, Any]:
    time.sleep(0.118)
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
    time.sleep(0.287)
    device = _TELEMETRY.get(device_id, {})

    # Device-level metrics (CPU, memory) returned when no interface specified
    if not interface:
        device_metrics = device.get("_device_metrics", {})
        interfaces = {k: v for k, v in device.items() if k != "_device_metrics"}
        anomaly = device_metrics.get("anomaly", False) or any(
            iface.get("out_errors", 0) > 500 or iface.get("utilization_pct", 0) > 90
            for iface in interfaces.values()
        )
        return {
            "device_id": device_id,
            "time_window": time_window,
            "device_metrics": device_metrics,
            "interfaces": interfaces,
            "anomaly": anomaly,
        }

    metrics = device.get(interface, {})
    # BGP flap with a known safe fix is an anomaly but NOT an escalation trigger.
    # Flag anomaly only for error/utilization spikes, not for config-fixable BGP state.
    anomaly = (
        metrics.get("out_errors", 0) > 500
        or metrics.get("utilization_pct", 0) > 90
        or metrics.get("crc_errors", 0) > 500
    )
    safe_to_remediate = bool(metrics.get("bgp_flap_count", 0) > 5 and not anomaly)
    result: dict[str, Any] = {
        "device_id": device_id,
        "interface": interface,
        "time_window": time_window,
        "metrics": metrics,
        "anomaly": anomaly,
    }
    if safe_to_remediate:
        result["safe_to_remediate"] = True
        result["remediation_note"] = metrics.get("note", "")
    return result
