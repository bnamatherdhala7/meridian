"""
Splunk MCP client — calls real Splunk MCP tools via HTTP when configured.
Falls back to realistic mock data when SPLUNK_MCP_URL is not set.
CI Catalyst calls are always mocked unless CI_CATALYST_URL is set.
"""
import httpx
import json
from vigil.config import SPLUNK_MCP_URL, SPLUNK_TOKEN, USE_MOCK_CI

HEADERS = {
    "Authorization": f"Bearer {SPLUNK_TOKEN}",
    "Content-Type":  "application/json",
}
TIMEOUT = 30.0

USE_MOCK_SPLUNK = not SPLUNK_MCP_URL


# ── Mock Splunk responses keyed by device ────────────────────────────────────

_MOCK_SPL_RESULTS = {
    "sw-core-01": {
        "splunk_run_query": {
            "result_count": 4,
            "events": [
                {"src_ip": "192.168.4.17", "drops": 14821, "bytes": 20800000, "drop_pct": 71.2, "out_errors": 312},
                {"src_ip": "10.14.0.5",    "drops": 891,   "bytes": 4200000,  "drop_pct": 17.5, "out_errors": 4},
                {"src_ip": "10.14.0.8",    "drops": 203,   "bytes": 1900000,  "drop_pct": 8.1,  "out_errors": 1},
                {"src_ip": "10.14.0.12",   "drops": 88,    "bytes": 900000,   "drop_pct": 3.2,  "out_errors": 0},
            ],
            "stats": {
                "anomaly": True,
                "dominant_src_ip": "192.168.4.17",
                "dominant_pct": 71.2,
                "threat_intel_match": True,
                "threat_score": 8.4,
                "dest_ip": "45.89.201.4",
                "dest_reputation": "known_c2",
            }
        },
        "saia_generate_spl": {
            "spl": "index=netops sourcetype=interface_stats device=\"sw-core-01\" earliest=-15m | stats sum(bytes) as total by src_ip | eventstats sum(total) as grand | eval pct=round(total/grand*100,1) | where pct > 50 | join src_ip [search index=threat_intel] | sort -pct",
            "explanation": "Egress concentration query with threat intel join to identify dominant source IP and check against known bad actors."
        },
        "splunk_get_knowledge_objects": {
            "saved_searches": [
                {"name": "NOC - High Egress Concentration", "match": True},
                {"name": "SOC - Threat Intel IP Match",     "match": True},
            ]
        },
    },
    "edge-rt-02": {
        "splunk_run_query": {
            "result_count": 3,
            "events": [
                {"peer": "upstream-isp-01", "flaps": 3, "reasons": ["keepalive_timeout"], "_time": "2024-02-14T14:30:00Z"},
                {"peer": "upstream-isp-01", "flaps": 1, "reasons": ["hold_timer_expired"], "_time": "2024-02-14T14:15:00Z"},
                {"peer": "upstream-isp-01", "flaps": 1, "reasons": ["keepalive_timeout"], "_time": "2024-02-14T14:00:00Z"},
            ],
            "stats": {
                "anomaly": True,
                "root_cause": "keepalive_timer_mismatch",
                "keepalive_local": 60,
                "keepalive_peer": 30,
                "is_security_threat": False,
                "safe_fix": "set bgp timers 30 90 on edge-rt-02",
                "flap_count": 5,
            }
        },
        "saia_generate_spl": {
            "spl": "index=netops sourcetype=bgp_events device=\"edge-rt-02\" earliest=-2h | stats count as flaps, values(reason) as reasons by peer | where flaps >= 2 | join peer [search index=netops sourcetype=bgp_config | table peer keepalive_timer peer_keepalive]",
            "explanation": "BGP flap detection with keepalive config join to identify timer mismatch root cause."
        },
        "splunk_get_knowledge_objects": {
            "saved_searches": [
                {"name": "NOC - BGP Peer Instability",     "match": True},
                {"name": "NOC - BGP Timer Configuration",  "match": True},
            ]
        },
    },
    "core-sw-03": {
        "splunk_run_query": {
            "result_count": 5,
            "events": [
                {"process": "unknown_pid_44821", "peak_cpu": 61.3, "user": "root",      "net_connections": 14, "file_writes": 203},
                {"process": "bgp",               "peak_cpu": 18.2, "user": "bgpd",      "net_connections": 4,  "file_writes": 0},
                {"process": "snmpd",             "peak_cpu": 8.1,  "user": "snmp",      "net_connections": 2,  "file_writes": 0},
                {"process": "syslogd",           "peak_cpu": 4.0,  "user": "syslog",    "net_connections": 1,  "file_writes": 88},
                {"process": "ntp",               "peak_cpu": 2.4,  "user": "ntp",       "net_connections": 1,  "file_writes": 0},
            ],
            "stats": {
                "anomaly": True,
                "unknown_process": True,
                "pid": 44821,
                "tor_connections": 3,
                "external_dest_ips": ["185.220.101.4", "185.220.100.252"],
                "is_security_threat": True,
                "note": "Process has active connections to known Tor exit nodes. Possible malware or crypto miner.",
            }
        },
        "saia_generate_spl": {
            "spl": "index=netops sourcetype=process_audit pid=44821 OR parent_pid=44821 | table _time pid parent_pid user cmd net_connections file_writes | join [search index=threat_intel src_ip IN (185.220.101.4, 185.220.100.252)] | sort _time",
            "explanation": "Unknown process audit with Tor exit node correlation to assess security threat level."
        },
        "splunk_get_knowledge_objects": {
            "saved_searches": [
                {"name": "SOC - Unknown Process Network Activity", "match": True},
                {"name": "SOC - Tor Exit Node Connections",        "match": True},
            ]
        },
    },
}

_DEFAULT_SPL_RESULT = {
    "splunk_run_query":           {"result_count": 0, "events": [], "stats": {"anomaly": False}},
    "saia_generate_spl":          {"spl": "index=netops | head 10", "explanation": "Generic fallback query."},
    "splunk_get_knowledge_objects": {"saved_searches": []},
}


def _mock_device(spl_or_prompt: str) -> str:
    """Infer which device mock to use from the query/prompt text."""
    text = spl_or_prompt.lower()
    if "sw-core-01" in text or "192.168.4.17" in text or "packet" in text:
        return "sw-core-01"
    if "edge-rt-02" in text or "bgp" in text or "keepalive" in text:
        return "edge-rt-02"
    if "core-sw-03" in text or "cpu" in text or "unknown process" in text:
        return "core-sw-03"
    return "__default__"


def _mock_splunk(tool: str, arguments: dict) -> dict:
    hint  = arguments.get("search") or arguments.get("prompt") or ""
    device = _mock_device(hint)
    bucket = _MOCK_SPL_RESULTS.get(device, _DEFAULT_SPL_RESULT)
    return bucket.get(tool, _DEFAULT_SPL_RESULT.get(tool, {}))


# ── Real MCP call ─────────────────────────────────────────────────────────────

def _mcp_call(tool: str, arguments: dict) -> dict:
    if USE_MOCK_SPLUNK:
        return _mock_splunk(tool, arguments)
    payload = {
        "jsonrpc": "2.0",
        "id":      1,
        "method":  "tools/call",
        "params":  {"name": tool, "arguments": arguments}
    }
    with httpx.Client(timeout=TIMEOUT, verify=False) as client:
        resp = client.post(SPLUNK_MCP_URL, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
    if "error" in data:
        raise RuntimeError(f"MCP error: {data['error']}")
    content = data.get("result", {}).get("content", [])
    text = " ".join(c.get("text", "") for c in content if c.get("type") == "text")
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


# ── Splunk platform tools (splunk_*) ──────────────────────────────────────────

def run_splunk_query(spl: str, earliest: str = "-15m", latest: str = "now") -> dict:
    return _mcp_call("splunk_run_query", {
        "search":        spl,
        "earliest_time": earliest,
        "latest_time":   latest,
        "max_results":   100
    })


def get_indexes() -> dict:
    return _mcp_call("splunk_get_indexes", {})


def get_knowledge_objects(query: str, object_type: str = "savedsearches") -> dict:
    return _mcp_call("splunk_get_knowledge_objects", {
        "search":      query,
        "object_type": object_type
    })


def get_splunk_info() -> dict:
    return _mcp_call("splunk_get_splunk_info", {})


# ── SAIA tools (saia_*) ───────────────────────────────────────────────────────

def generate_spl(prompt: str, context: dict = None) -> dict:
    args: dict = {"prompt": prompt}
    if context:
        args["context"] = json.dumps(context)
    return _mcp_call("saia_generate_spl", args)


def explain_spl(spl: str) -> dict:
    return _mcp_call("saia_explain_spl", {"search": spl})


def optimize_spl(spl: str) -> dict:
    return _mcp_call("saia_optimize_spl", {"search": spl})


# ── CI Catalyst tools (ci_*) — real or mock ───────────────────────────────────

_MOCK_TOPOLOGY = {
    "sw-core-01": {"upstream": "core-rt-01",     "vlan": [100, 200],       "downstream_count": 14, "blast_radius": "HIGH",     "position": "core"},
    "edge-rt-02": {"upstream": "upstream-isp-01", "vlan": [10],            "downstream_count": 2,  "blast_radius": "LOW",      "position": "edge"},
    "core-sw-03": {"upstream": "core-rt-02",     "vlan": [100, 200, 300],  "downstream_count": 31, "blast_radius": "CRITICAL", "position": "core"},
}

_MOCK_TELEMETRY = {
    "sw-core-01": {"cpu_pct": 34, "mem_pct": 61, "tx_gbps": 9.8, "rx_gbps": 1.2, "drops": 14821, "errors": 0},
    "edge-rt-02": {"cpu_pct": 18, "mem_pct": 44, "bgp_state": "ESTABLISHED", "keepalive_local": 60, "keepalive_peer": 30},
    "core-sw-03": {"cpu_pct": 94, "mem_pct": 78, "drops": 0, "errors": 0, "unknown_processes": ["PID 44821"]},
}


def get_network_topology(device: str) -> dict:
    if not USE_MOCK_CI:
        from vigil.config import CI_CATALYST_URL, CI_CATALYST_TOKEN
        resp = httpx.get(f"{CI_CATALYST_URL}/topology/{device}",
                         headers={"X-Auth-Token": CI_CATALYST_TOKEN}, timeout=TIMEOUT)
        return resp.json()
    return _MOCK_TOPOLOGY.get(device, {"device": device, "blast_radius": "UNKNOWN", "downstream_count": 0})


def get_telemetry_metrics(device: str, interface: str = None) -> dict:
    if not USE_MOCK_CI:
        from vigil.config import CI_CATALYST_URL, CI_CATALYST_TOKEN
        url = f"{CI_CATALYST_URL}/telemetry/{device}"
        if interface:
            url += f"/{interface}"
        resp = httpx.get(url, headers={"X-Auth-Token": CI_CATALYST_TOKEN}, timeout=TIMEOUT)
        return resp.json()
    return _MOCK_TELEMETRY.get(device, {"device": device, "cpu_pct": 0, "mem_pct": 0})
