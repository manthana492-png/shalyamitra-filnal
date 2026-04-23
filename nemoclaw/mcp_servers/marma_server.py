"""
ShalyaMitra — Marma MCP Server

Model Context Protocol server that exposes the 107 Marma database
as tools that NemoClaw agents can invoke.

Tools:
  - lookup_marma_for_procedure(procedure) → relevant Marma points
  - get_critical_marmas() → 19 Sadya Pranahara points
  - get_marma_by_zone(zone) → spatial anatomy lookup
  - get_marma_by_id(id) → single Marma detail
  - get_marma_stats() → database statistics

MCP protocol: https://modelcontextprotocol.io
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from app.knowledge.marma_db import (
    MARMA_DB, get_marma_for_procedure, get_marma_by_id,
    get_marma_by_zone, get_marma_by_classification,
    get_critical_marmas, get_marma_stats,
)

MCP_TOOLS = {
    "lookup_marma_for_procedure": {
        "description": "Get Marma vital points relevant to a surgical procedure. Returns points that are at risk during the specified surgery with protective doctrine.",
        "parameters": {
            "type": "object",
            "properties": {
                "procedure": {"type": "string", "description": "Surgical procedure name, e.g. 'Cholecystectomy', 'Thyroidectomy'"}
            },
            "required": ["procedure"]
        },
    },
    "get_critical_marmas": {
        "description": "Get all 19 Sadya Pranahara (immediately fatal) Marma points. These are the highest-risk anatomical zones in any surgery.",
        "parameters": {"type": "object", "properties": {}},
    },
    "get_marma_by_zone": {
        "description": "Get Marma points near a specific anatomical zone or structure, e.g. 'carotid', 'axilla', 'umbilical'.",
        "parameters": {
            "type": "object",
            "properties": {
                "zone": {"type": "string", "description": "Anatomical zone or structure name"}
            },
            "required": ["zone"]
        },
    },
    "get_marma_by_id": {
        "description": "Get detailed information about a specific Marma point by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "marma_id": {"type": "string", "description": "Marma ID, e.g. 'adhipati', 'hridaya', 'nabhi'"}
            },
            "required": ["marma_id"]
        },
    },
    "get_marma_stats": {
        "description": "Get summary statistics of the Marma database — counts by classification and region.",
        "parameters": {"type": "object", "properties": {}},
    },
}


def execute_tool(tool_name: str, args: dict) -> dict:
    """Execute an MCP tool call and return results."""
    if tool_name == "lookup_marma_for_procedure":
        results = get_marma_for_procedure(args["procedure"])
        return {"procedure": args["procedure"], "count": len(results), "marmas": results}

    elif tool_name == "get_critical_marmas":
        results = get_critical_marmas()
        return {"classification": "Sadya Pranahara", "count": len(results), "marmas": results}

    elif tool_name == "get_marma_by_zone":
        results = get_marma_by_zone(args["zone"])
        return {"zone": args["zone"], "count": len(results), "marmas": results}

    elif tool_name == "get_marma_by_id":
        result = get_marma_by_id(args["marma_id"])
        return result or {"error": f"Marma '{args['marma_id']}' not found"}

    elif tool_name == "get_marma_stats":
        return get_marma_stats()

    return {"error": f"Unknown tool: {tool_name}"}


class MCPHandler(BaseHTTPRequestHandler):
    """Simple HTTP-based MCP server handler."""

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_len))

        if self.path == "/tools/list":
            response = {"tools": [
                {"name": name, **spec} for name, spec in MCP_TOOLS.items()
            ]}
        elif self.path == "/tools/call":
            tool_name = body.get("name", "")
            arguments = body.get("arguments", {})
            result = execute_tool(tool_name, arguments)
            response = {"content": [{"type": "text", "text": json.dumps(result, default=str, ensure_ascii=False)}]}
        else:
            response = {"error": "Unknown endpoint"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, default=str, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[MCP-Marma] {args[0]}")


if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 3001))
    server = HTTPServer(("0.0.0.0", port), MCPHandler)
    print(f"[MCP-Marma] Serving 107 Marma points on port {port}")
    server.serve_forever()
