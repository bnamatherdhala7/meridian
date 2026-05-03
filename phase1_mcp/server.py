"""MCP server — wraps all tools for real MCP client connections.

Run standalone:  python -m phase1_mcp.server
Then connect any MCP client to the stdio transport.
The commander uses the tool functions directly; this server enables
external MCP clients (e.g. Claude Desktop, other agents) to use the same tools.
"""
from mcp.server.fastmcp import FastMCP

from phase1_mcp.tools.cisco import get_network_topology, get_telemetry_metrics
from phase1_mcp.tools.splunk import (
    generate_spl,
    get_knowledge_objects,
    run_spl_query,
    search_indexes,
)

mcp = FastMCP("vigil")


@mcp.tool()
def run_spl_query_tool(spl: str, index: str = "*", time_window: str = "last 30 minutes") -> dict:
    """Execute an SPL query against SP indexes. Returns matching events and statistics."""
    return run_spl_query(spl, index, time_window)


@mcp.tool()
def generate_spl_tool(natural_language: str, index: str = "network_telemetry") -> dict:
    """Generate an optimized SPL query from a natural language description."""
    return generate_spl(natural_language, index)


@mcp.tool()
def search_indexes_tool(query: str = "") -> dict:
    """Discover available SP indexes and their metadata."""
    return search_indexes(query)


@mcp.tool()
def get_knowledge_objects_tool(object_type: str = "all") -> dict:
    """Surface saved searches, field extractions, and lookups from SP."""
    return get_knowledge_objects(object_type)


@mcp.tool()
def get_network_topology_tool(site: str = "", device_id: str = "") -> dict:
    """Get CI Catalyst network topology — device graph and inter-device links."""
    return get_network_topology(site, device_id)


@mcp.tool()
def get_telemetry_metrics_tool(
    device_id: str,
    interface: str = "",
    time_window: str = "last 5 minutes",
) -> dict:
    """Get real-time interface-level telemetry metrics from a CI device."""
    return get_telemetry_metrics(device_id, interface, time_window)


if __name__ == "__main__":
    mcp.run()
