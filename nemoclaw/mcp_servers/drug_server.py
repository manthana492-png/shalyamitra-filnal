"""
ShalyaMitra — Drug Database MCP Server

MCP server exposing the pharmacological database for NemoClaw agents.

Tools:
  - check_drug_interaction(drug_a, drug_b) → interaction severity + advice
  - calculate_dose(drug, weight_kg) → weight-based dosing
  - get_drug_info(drug_name) → full drug profile
  - list_all_drugs() → all 16 drugs in database
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from app.knowledge.drug_db import DRUG_DB, INTERACTION_DB

MCP_TOOLS = {
    "check_drug_interaction": {
        "description": "Check for interactions between two surgical drugs. Returns severity (major/moderate/minor) and clinical advice.",
        "parameters": {
            "type": "object",
            "properties": {
                "drug_a": {"type": "string", "description": "First drug name"},
                "drug_b": {"type": "string", "description": "Second drug name"}
            },
            "required": ["drug_a", "drug_b"]
        },
    },
    "calculate_dose": {
        "description": "Calculate weight-based drug dosing for a patient.",
        "parameters": {
            "type": "object",
            "properties": {
                "drug": {"type": "string", "description": "Drug name"},
                "weight_kg": {"type": "number", "description": "Patient weight in kg"},
                "renal_function": {"type": "string", "description": "normal/mild/moderate/severe", "default": "normal"}
            },
            "required": ["drug", "weight_kg"]
        },
    },
    "get_drug_info": {
        "description": "Get full pharmacological profile of a drug including class, mechanism, onset, duration, side effects.",
        "parameters": {
            "type": "object",
            "properties": {
                "drug_name": {"type": "string", "description": "Drug name"}
            },
            "required": ["drug_name"]
        },
    },
    "list_all_drugs": {
        "description": "List all drugs in the surgical pharmacological database.",
        "parameters": {"type": "object", "properties": {}},
    },
}


def find_drug(name: str) -> dict | None:
    name_lower = name.lower()
    for drug in DRUG_DB:
        if drug["name"].lower() == name_lower or name_lower in drug.get("aliases", []):
            return drug
    return None


def check_interaction(drug_a: str, drug_b: str) -> dict:
    a_lower, b_lower = drug_a.lower(), drug_b.lower()
    for interaction in INTERACTION_DB:
        pair = {interaction["drug_a"].lower(), interaction["drug_b"].lower()}
        if {a_lower, b_lower} == pair:
            return interaction
    return {"result": "no_interaction", "drug_a": drug_a, "drug_b": drug_b,
            "message": "No known interaction in database"}


def calculate_dose(drug_name: str, weight_kg: float, renal: str = "normal") -> dict:
    drug = find_drug(drug_name)
    if not drug:
        return {"error": f"Drug '{drug_name}' not found"}
    dose_info = drug.get("dosing", {})
    dose_per_kg = dose_info.get("mg_per_kg", 0)
    max_dose = dose_info.get("max_mg", 0)

    calculated = round(dose_per_kg * weight_kg, 1) if dose_per_kg else 0
    if max_dose and calculated > max_dose:
        calculated = max_dose

    renal_adj = {"normal": 1.0, "mild": 0.75, "moderate": 0.5, "severe": 0.25}
    factor = renal_adj.get(renal, 1.0)
    adjusted = round(calculated * factor, 1)

    return {
        "drug": drug_name, "weight_kg": weight_kg,
        "base_dose_mg": calculated, "renal_adjustment": factor,
        "adjusted_dose_mg": adjusted, "max_dose_mg": max_dose,
        "route": dose_info.get("route", "IV"),
        "note": f"Renal adjustment applied: {renal}" if factor < 1 else "No renal adjustment needed",
    }


def execute_tool(tool_name: str, args: dict) -> dict:
    if tool_name == "check_drug_interaction":
        return check_interaction(args["drug_a"], args["drug_b"])
    elif tool_name == "calculate_dose":
        return calculate_dose(args["drug"], args["weight_kg"], args.get("renal_function", "normal"))
    elif tool_name == "get_drug_info":
        drug = find_drug(args["drug_name"])
        return drug or {"error": f"Drug '{args['drug_name']}' not found"}
    elif tool_name == "list_all_drugs":
        return {"count": len(DRUG_DB), "drugs": [d["name"] for d in DRUG_DB]}
    return {"error": f"Unknown tool: {tool_name}"}


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_len))
        if self.path == "/tools/list":
            response = {"tools": [{"name": n, **s} for n, s in MCP_TOOLS.items()]}
        elif self.path == "/tools/call":
            result = execute_tool(body.get("name", ""), body.get("arguments", {}))
            response = {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}
        else:
            response = {"error": "Unknown endpoint"}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, default=str).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[MCP-Drug] {args[0]}")


if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 3002))
    server = HTTPServer(("0.0.0.0", port), MCPHandler)
    print(f"[MCP-Drug] Serving {len(DRUG_DB)} drugs + {len(INTERACTION_DB)} interactions on port {port}")
    server.serve_forever()
