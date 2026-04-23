"""
ShalyaMitra — Safety MCP Server

MCP server exposing PHI redaction and clinical guardrails
as tools for NemoClaw agents.

Tools:
  - redact_phi(text) → cleaned text with PHI masked
  - check_guardrails(text, agent_type) → safe version
  - get_safety_stats() → audit statistics
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json, asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from app.safety.phi_redaction import get_phi_engine, RedactionMode
from app.safety.clinical_guardrails import ClinicalGuardrailsEngine

MCP_TOOLS = {
    "redact_phi": {
        "description": "Redact Protected Health Information (PHI) and PII from text. Detects Aadhaar, PAN, ABHA, patient names, phone numbers, emails, MRN, addresses. Returns cleaned text safe for cloud transmission.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to redact PHI from"},
                "mode": {"type": "string", "enum": ["mask", "hash", "partial"], "default": "mask"}
            },
            "required": ["text"]
        },
    },
    "check_guardrails": {
        "description": "Run clinical safety guardrails on AI-generated text. Blocks unsafe dosing commands, softens direct surgical instructions, detects PHI leaks and hallucinations.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "AI response text to check"},
                "agent_type": {"type": "string", "description": "Which agent generated this", "default": "unknown"}
            },
            "required": ["text"]
        },
    },
    "get_safety_stats": {
        "description": "Get audit statistics for PHI detections and guardrail triggers.",
        "parameters": {"type": "object", "properties": {}},
    },
}

_guardrails = ClinicalGuardrailsEngine(enable_llm_validation=False)


def execute_tool(tool_name: str, args: dict) -> dict:
    if tool_name == "redact_phi":
        mode_str = args.get("mode", "mask")
        mode = RedactionMode(mode_str) if mode_str in [m.value for m in RedactionMode] else RedactionMode.MASK
        engine = get_phi_engine(mode)
        result = engine.redact(args["text"])
        return {
            "redacted_text": result.redacted_text,
            "phi_detected": result.phi_detected,
            "categories_found": result.categories_found,
            "match_count": len(result.matches),
        }
    elif tool_name == "check_guardrails":
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            _guardrails.check(args["text"], agent_type=args.get("agent_type", "unknown"), skip_llm=True)
        )
        return {
            "safe_text": result.safe_text,
            "outcome": result.outcome.value,
            "violations": [{"rule": v.rule_name, "severity": v.severity} for v in result.violations],
            "caveats": result.caveats_added,
        }
    elif tool_name == "get_safety_stats":
        return {
            "guardrails": _guardrails.get_stats(),
        }
    return {"error": f"Unknown tool: {tool_name}"}


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_len))
        if self.path == "/tools/list":
            response = {"tools": [{"name": n, **s} for n, s in MCP_TOOLS.items()]}
        elif self.path == "/tools/call":
            result = execute_tool(body.get("name", ""), body.get("arguments", {}))
            response = {"content": [{"type": "text", "text": json.dumps(result, default=str, ensure_ascii=False)}]}
        else:
            response = {"error": "Unknown endpoint"}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, default=str, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[MCP-Safety] {args[0]}")


if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 3003))
    server = HTTPServer(("0.0.0.0", port), MCPHandler)
    print(f"[MCP-Safety] PHI Redaction + Clinical Guardrails on port {port}")
    server.serve_forever()
