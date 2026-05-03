"""Mocked SP MCP tools — same interface as real Splunk GA MCP server.

Tool name mapping to Splunk MCP v1.1 (GA):
  run_spl_query      → splunk_run_query
  search_indexes     → splunk_get_indexes
  get_knowledge_objects → splunk_get_knowledge_objects
  generate_spl       → saia_generate_spl
  get_metadata       → splunk_get_metadata
  get_user_context   → splunk_get_user_info

Swap mode to "live" in config.yaml + set SP_ENDPOINT + SP_TOKEN env vars
to connect to a real Splunk instance without changing any other code.
"""
import time
from typing import Any

_INDEXES = [
    {"name": "network_telemetry", "size_mb": 45200, "event_count": 2847000,
     "earliest": "2024-01-01", "latest": "2024-02-15"},
    {"name": "security_logs", "size_mb": 12800, "event_count": 891000,
     "earliest": "2024-01-01", "latest": "2024-02-15"},
    {"name": "ise_logs", "size_mb": 3200, "event_count": 234000,
     "earliest": "2024-01-01", "latest": "2024-02-15"},
    {"name": "netflow", "size_mb": 78900, "event_count": 15600000,
     "earliest": "2024-01-01", "latest": "2024-02-15"},
    {"name": "routing_logs", "size_mb": 8400, "event_count": 1240000,
     "earliest": "2024-01-01", "latest": "2024-02-15"},
    {"name": "syslog", "size_mb": 22100, "event_count": 8900000,
     "earliest": "2024-01-01", "latest": "2024-02-15"},
]

_KNOWLEDGE_OBJECTS = [
    {"type": "saved_search", "name": "Interface Error Spike Alert",
     "search": "index=network_telemetry out_errors>1000"},
    {"type": "saved_search", "name": "BGP Session Down Alert",
     "search": "index=routing_logs event_type=bgp_session_down"},
    {"type": "saved_search", "name": "High CPU Alert",
     "search": "index=syslog cpu_utilization>90"},
    {"type": "field_extraction", "name": "ci_interface_parser",
     "fields": ["device_id", "interface", "in_errors", "out_errors", "drops"]},
    {"type": "field_extraction", "name": "bgp_event_parser",
     "fields": ["device_id", "peer_ip", "event_type", "reason", "session_state"]},
    {"type": "lookup", "name": "device_inventory",
     "fields": ["device_id", "hostname", "site", "model", "role"]},
    {"type": "lookup", "name": "user_ip_map",
     "fields": ["src_ip", "username", "department", "is_privileged"]},
]

# ── Packet loss (Scenario A) ────────────────────────────────────────────────

_INTERFACE_RESULT = {
    "events": [
        {"_time": "2024-02-14T14:32:00Z", "device_id": "sj-catalyst-01", "interface": "GigE0/1",
         "in_errors": 12, "out_errors": 2847, "drops": 1923, "utilization_pct": 94.2, "vlan": 100},
        {"_time": "2024-02-14T14:30:00Z", "device_id": "sj-catalyst-01", "interface": "GigE0/1",
         "in_errors": 8, "out_errors": 2634, "drops": 1701, "utilization_pct": 91.8, "vlan": 100},
        {"_time": "2024-02-14T14:28:00Z", "device_id": "sj-catalyst-01", "interface": "GigE0/1",
         "in_errors": 5, "out_errors": 312, "drops": 89, "utilization_pct": 42.1, "vlan": 100},
    ],
    "stats": {
        "avg_out_errors": 1931, "avg_drops": 1238,
        "spike_at": "2024-02-14T14:30:00Z", "duration_mins": 4,
        "note": "Asymmetric error pattern: out_errors >> in_errors suggests egress congestion",
    },
}

_EGRESS_RESULT = {
    "events": [
        {"src_ip": "10.14.22.87", "bytes_out": 8947234, "pct_of_egress": 71.2,
         "dest_ip_count": 847, "protocol": "TCP", "port_spread": "high"},
        {"src_ip": "10.14.22.12", "bytes_out": 1203847, "pct_of_egress": 9.6,
         "dest_ip_count": 12, "protocol": "TCP"},
        {"src_ip": "10.14.22.45", "bytes_out": 987234, "pct_of_egress": 7.9,
         "dest_ip_count": 8, "protocol": "UDP"},
    ],
    "stats": {
        "total_bytes": 12567891, "top_src": "10.14.22.87", "top_src_pct": 71.2,
        "anomaly": "Single host accounts for 71.2% of egress — threshold is 60%",
    },
}

# ── BGP flap (Scenario B) ───────────────────────────────────────────────────

_BGP_EVENTS_RESULT = {
    "events": [
        {"_time": "2024-02-15T14:30:00Z", "device_id": "sj-edge-01", "interface": "GigE0/0",
         "event_type": "bgp_session_down", "peer_ip": "203.0.113.1", "reason": "hold_timer_expired",
         "session_state": "Idle", "flap_count": 23},
        {"_time": "2024-02-15T14:28:00Z", "device_id": "sj-edge-01", "interface": "GigE0/0",
         "event_type": "bgp_session_up", "peer_ip": "203.0.113.1", "reason": "session_established",
         "session_state": "Established", "flap_count": 22},
        {"_time": "2024-02-15T14:26:00Z", "device_id": "sj-edge-01", "interface": "GigE0/0",
         "event_type": "bgp_session_down", "peer_ip": "203.0.113.1", "reason": "hold_timer_expired",
         "session_state": "Idle", "flap_count": 21},
    ],
    "stats": {
        "flap_count": 23, "peer_ip": "203.0.113.1", "first_flap_at": "2024-02-15T14:05:00Z",
        "avg_session_duration_secs": 68,
        "note": "Hold timer expiry pattern consistent with MTU mismatch — BGP keepalives dropped",
    },
}

_MTU_RESULT = {
    "events": [
        {"_time": "2024-02-15T14:05:00Z", "device_id": "sj-edge-01", "interface": "GigE0/0",
         "local_mtu": 1500, "negotiated_mtu": 1480, "mtu_error": "path_mtu_too_large",
         "peer_ip": "203.0.113.1"},
    ],
    "stats": {
        "local_mtu": 1500, "required_mtu": 1480,
        "cause": "ISP MPLS overhead requires MTU 1480 — local interface configured at 1500",
        "safe_fix": "ip mtu 1480 on GigE0/0 — known safe config change, reversible",
        "anomaly": "MTU mismatch confirmed: sj-edge-01 GigE0/0 must be set to 1480",
    },
}

# ── CPU spike (Scenario C) ──────────────────────────────────────────────────

_CPU_PROCESS_RESULT = {
    "events": [
        {"_time": "2024-02-15T15:12:00Z", "device_id": "sj-core-01", "cpu_pct": 94.1,
         "process": "BGP Scanner", "pid": 12401, "process_cpu_pct": 42.1},
        {"_time": "2024-02-15T15:12:00Z", "device_id": "sj-core-01", "cpu_pct": 94.1,
         "process": "Spanning Tree", "pid": 12244, "process_cpu_pct": 28.3},
        {"_time": "2024-02-15T15:12:00Z", "device_id": "sj-core-01", "cpu_pct": 94.1,
         "process": "unknown", "pid": 14847, "process_cpu_pct": 23.7},
    ],
    "stats": {
        "avg_cpu_pct": 94.1, "spike_at": "2024-02-15T14:54:00Z", "duration_mins": 18,
        "top_process": "BGP Scanner", "unknown_pid": 14847, "unknown_pct": 23.7,
        "note": "Unknown PID 14847 consuming 23.7% — identity unresolved, may be malicious or runaway",
    },
}

_CPU_HISTORY_RESULT = {
    "events": [
        {"_time": "2024-01-22T09:14:00Z", "device_id": "sj-core-01", "cpu_pct": 91.2,
         "resolved_by": "device_reload", "resolution_time_mins": 47,
         "risk_note": "Reload caused 3-minute BGP reconvergence affecting all downstream devices"},
    ],
    "stats": {
        "prior_incidents": 1, "last_incident_at": "2024-01-22T09:14:00Z",
        "last_resolution": "device_reload",
        "warning": "Prior reload on sj-core-01 caused 3-min outage for all downstream — high blast radius",
    },
}


def run_spl_query(spl: str, index: str = "*", time_window: str = "last 30 minutes") -> dict[str, Any]:
    time.sleep(0.38 + (hash(spl) % 100) / 1000)
    spl_lower = spl.lower()
    # BGP/routing keywords — check before generic interface
    if any(k in spl_lower for k in ("bgp", "session_down", "hold_timer", "routing_logs", "peer_ip", "flap")):
        return {"query": spl, **_BGP_EVENTS_RESULT}
    # MTU keywords
    if any(k in spl_lower for k in ("mtu", "path_mtu", "negotiated_mtu", "mtu_error")):
        return {"query": spl, **_MTU_RESULT}
    # CPU/process keywords
    if any(k in spl_lower for k in ("cpu", "cpu_pct", "process_cpu", "pid", "cpu_utilization")):
        if any(k in spl_lower for k in ("history", "prior", "last 30 days", "last 7 days", "month")):
            return {"query": spl, **_CPU_HISTORY_RESULT}
        return {"query": spl, **_CPU_PROCESS_RESULT}
    # Egress/netflow keywords — check before generic interface
    if any(k in spl_lower for k in ("src_ip", "bytes_out", "egress", "netflow", "sum(bytes", "top_src")):
        return {"query": spl, **_EGRESS_RESULT}
    # Interface error keywords
    if any(k in spl_lower for k in ("out_errors", "in_errors", "drops", "avg(out_errors", "avg(drops", "gige0/1")):
        return {"query": spl, **_INTERFACE_RESULT}
    return {"query": spl, "events": [], "stats": {"message": "No events matched."}}


def generate_spl(natural_language: str, index: str = "network_telemetry") -> dict[str, Any]:
    time.sleep(0.12)
    nl = natural_language.lower()
    if any(k in nl for k in ("bgp", "peer", "session", "routing")):
        return {
            "spl": (
                'index=routing_logs device_id="sj-edge-01" '
                '| stats count as flap_count, latest(session_state) as state by peer_ip, event_type '
                '| where event_type="bgp_session_down"'
            ),
            "explanation": "Counts BGP session down events per peer to identify flapping sessions.",
            "estimated_events": 23,
        }
    if any(k in nl for k in ("cpu", "process", "utilization")):
        return {
            "spl": (
                'index=syslog device_id="sj-core-01" '
                '| stats avg(cpu_pct) as avg_cpu, max(cpu_pct) as peak_cpu by _time span=1m '
                '| where avg_cpu > 80'
            ),
            "explanation": "Tracks CPU utilization over time to find spike onset.",
            "estimated_events": 18,
        }
    if any(k in nl for k in ("error", "drop", "packet loss", "interface", "gige")):
        return {
            "spl": (
                f'index={index} device_id="sj-catalyst-01" interface="GigE0/1" '
                f'| stats avg(out_errors) as avg_errors, avg(drops) as avg_drops by _time span=2m '
                f'| where avg_errors > 100'
            ),
            "explanation": "Queries interface error counters aggregated in 2-minute buckets.",
            "estimated_events": 1200,
        }
    if any(k in nl for k in ("traffic", "egress", "src_ip", "bandwidth")):
        return {
            "spl": (
                'index=netflow device_id="sj-catalyst-01" interface="GigE0/1" direction=egress '
                '| stats sum(bytes_out) as bytes_out by src_ip '
                '| eval pct_of_egress=round(bytes_out/sum(bytes_out)*100,1) | sort -bytes_out'
            ),
            "explanation": "Aggregates egress traffic by source IP to identify dominant talkers.",
            "estimated_events": 340,
        }
    return {
        "spl": f"index={index} | head 100",
        "explanation": "General query — refine with specific fields.",
        "estimated_events": 100,
    }


def search_indexes(query: str = "") -> dict[str, Any]:
    time.sleep(0.042)
    return {"indexes": _INDEXES, "total": len(_INDEXES)}


def get_knowledge_objects(object_type: str = "all") -> dict[str, Any]:
    time.sleep(0.09)
    return {"objects": _KNOWLEDGE_OBJECTS, "total": len(_KNOWLEDGE_OBJECTS)}


def get_metadata(index: str = "*", metadata_type: str = "hosts") -> dict[str, Any]:
    """Maps to splunk_get_metadata — discovers which hosts are generating events."""
    time.sleep(0.065)
    hosts_by_index = {
        "network_telemetry": ["sj-catalyst-01", "sj-core-01", "sj-edge-01"],
        "routing_logs":      ["sj-edge-01", "sj-core-01"],
        "syslog":            ["sj-core-01", "sj-catalyst-01", "sj-edge-01"],
        "netflow":           ["sj-catalyst-01"],
        "security_logs":     ["sj-catalyst-01"],
        "ise_logs":          ["ise-01"],
    }
    if index != "*" and index in hosts_by_index:
        hosts = hosts_by_index[index]
    else:
        seen: set[str] = set()
        hosts = [h for idx in hosts_by_index.values() for h in idx if not (h in seen or seen.add(h))]  # type: ignore[func-returns-value]
    return {
        "metadata_type": metadata_type,
        "index": index,
        "hosts": [
            {"host": "sj-catalyst-01", "event_count": 2847000, "last_event": "2024-02-15T15:12:00Z",
             "indexes": ["network_telemetry", "netflow", "security_logs"]},
            {"host": "sj-core-01", "event_count": 8920000, "last_event": "2024-02-15T15:12:00Z",
             "indexes": ["syslog", "network_telemetry", "routing_logs"],
             "alert": "cpu_utilization=94.1% — active alert"},
            {"host": "sj-edge-01", "event_count": 1240000, "last_event": "2024-02-15T15:12:00Z",
             "indexes": ["routing_logs", "syslog"],
             "alert": "bgp_flap_count=23 — active alert"},
        ] if index == "*" else [
            h for h in [
                {"host": "sj-catalyst-01", "event_count": 2847000},
                {"host": "sj-core-01", "event_count": 8920000},
                {"host": "sj-edge-01", "event_count": 1240000},
            ] if h["host"] in hosts
        ],
        "total_hosts": len(hosts),
    }


def get_user_context(src_ip: str = "", username: str = "") -> dict[str, Any]:
    """Maps to splunk_get_user_info — checks if a src_ip belongs to a known user."""
    time.sleep(0.078)
    _user_map = {
        "10.14.22.87": {
            "src_ip": "10.14.22.87", "username": None, "department": None,
            "is_privileged": False, "is_known": False,
            "threat_intel": "Not in corporate DHCP lease table — possible rogue device or spoofed IP",
            "recommendation": "Treat as unknown/untrusted — isolate pending threat intel lookup",
        },
        "10.14.22.12": {
            "src_ip": "10.14.22.12", "username": "jsmith", "department": "Engineering",
            "is_privileged": False, "is_known": True,
            "threat_intel": "Known corporate workstation — normal traffic pattern",
        },
    }
    if src_ip in _user_map:
        return _user_map[src_ip]
    return {
        "src_ip": src_ip, "username": username or None, "is_known": bool(username),
        "threat_intel": "No record found in user-IP mapping lookup",
    }
