#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
# slot-start.sh — Activate a ShalyaMitra surgery slot
# ══════════════════════════════════════════════════════════
# Run this on the Lightning AI GPU instance after it boots.
#
# What it does:
#   1. Detects the public IP of this Lightning AI instance
#   2. Updates Cloudflare DNS:  gpu.shalyamitra.quaasx108.com → this IP
#   3. Starts the full GPU Docker Compose stack
#   4. Waits for FastAPI health to be green
#   5. Prints the surgeon access URL
#
# Required environment variables (set in Lightning AI secrets):
#   CF_API_TOKEN     — Cloudflare API token (Zone:DNS:Edit)
#   CF_ZONE_ID       — Cloudflare Zone ID for quaasx108.com
#   CF_RECORD_NAME   — e.g. gpu.shalyamitra.quaasx108.com
#   COMPOSE_PROFILES — e.g. "nvidia" or leave empty for default
#
# Usage:
#   chmod +x scripts/slot-start.sh
#   ./scripts/slot-start.sh
# ══════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { echo -e "${CYAN}[slot-start]${NC} $*"; }
ok()   { echo -e "${GREEN}[slot-start]${NC} $*"; }
warn() { echo -e "${YELLOW}[slot-start]${NC} $*"; }
err()  { echo -e "${RED}[slot-start]${NC} $*"; exit 1; }

# ── Config ────────────────────────────────────────────────
CF_API_TOKEN="${CF_API_TOKEN:-}"
CF_ZONE_ID="${CF_ZONE_ID:-}"
CF_RECORD_NAME="${CF_RECORD_NAME:-gpu.shalyamitra.quaasx108.com}"
GPU_STACK_DIR="${GPU_STACK_DIR:-$(dirname "$0")/../gpu-stack}"
HEALTH_URL="http://localhost:80/healthz"
HEALTH_RETRIES=30
HEALTH_WAIT=10    # seconds between retries

# ── 1. Get public IP ─────────────────────────────────────
log "Detecting public IP..."
PUBLIC_IP=$(curl -sf https://api.ipify.org || curl -sf https://ifconfig.me)
[[ -z "$PUBLIC_IP" ]] && err "Could not detect public IP."
ok "Public IP: $PUBLIC_IP"

# ── 2. Update Cloudflare DNS record ──────────────────────
if [[ -z "$CF_API_TOKEN" || -z "$CF_ZONE_ID" ]]; then
    warn "CF_API_TOKEN or CF_ZONE_ID not set — skipping Cloudflare DNS update."
    warn "Manually set gpu.shalyamitra.quaasx108.com → $PUBLIC_IP in Cloudflare dashboard."
else
    log "Fetching existing DNS record for ${CF_RECORD_NAME}..."
    RECORD_RESPONSE=$(curl -sf -X GET \
        "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records?type=A&name=${CF_RECORD_NAME}" \
        -H "Authorization: Bearer ${CF_API_TOKEN}" \
        -H "Content-Type: application/json")

    RECORD_ID=$(echo "$RECORD_RESPONSE" | python3 -c "import sys,json; recs=json.load(sys.stdin)['result']; print(recs[0]['id'] if recs else '')" 2>/dev/null || true)

    DNS_PAYLOAD=$(python3 -c "import json; print(json.dumps({
        'type': 'A',
        'name': '${CF_RECORD_NAME}',
        'content': '${PUBLIC_IP}',
        'ttl': 60,
        'proxied': True
    }))")

    if [[ -n "$RECORD_ID" ]]; then
        log "Updating existing A record (ID: $RECORD_ID)..."
        curl -sf -X PUT \
            "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records/${RECORD_ID}" \
            -H "Authorization: Bearer ${CF_API_TOKEN}" \
            -H "Content-Type: application/json" \
            --data "$DNS_PAYLOAD" > /dev/null
    else
        log "Creating new A record..."
        curl -sf -X POST \
            "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records" \
            -H "Authorization: Bearer ${CF_API_TOKEN}" \
            -H "Content-Type: application/json" \
            --data "$DNS_PAYLOAD" > /dev/null
    fi
    ok "Cloudflare DNS updated: ${CF_RECORD_NAME} → ${PUBLIC_IP} (proxied)"
fi

# ── 3. Start GPU Docker Compose stack ────────────────────
log "Starting GPU stack from ${GPU_STACK_DIR}..."
cd "$GPU_STACK_DIR"

COMPOSE_CMD="docker compose -f docker-compose.gpu.yml"
[[ -n "${COMPOSE_PROFILES:-}" ]] && COMPOSE_CMD="$COMPOSE_CMD --profile ${COMPOSE_PROFILES}"

$COMPOSE_CMD up -d --build
ok "Docker Compose started."

# ── 4. Wait for FastAPI health ────────────────────────────
log "Waiting for FastAPI to be healthy (up to $((HEALTH_RETRIES * HEALTH_WAIT))s)..."
for i in $(seq 1 $HEALTH_RETRIES); do
    STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "000")
    if [[ "$STATUS" == "200" ]]; then
        ok "FastAPI healthy after $((i * HEALTH_WAIT))s."
        break
    fi
    if [[ "$i" -eq "$HEALTH_RETRIES" ]]; then
        err "FastAPI did not become healthy in time. Check logs: docker compose logs agent-orchestrator"
    fi
    echo "  attempt $i/$HEALTH_RETRIES (status=$STATUS) — waiting ${HEALTH_WAIT}s..."
    sleep "$HEALTH_WAIT"
done

# ── 5. Summary ────────────────────────────────────────────
echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ShalyaMitra slot is LIVE                   ${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "  GPU instance IP  : ${YELLOW}${PUBLIC_IP}${NC}"
echo -e "  Public API URL   : ${YELLOW}https://${CF_RECORD_NAME}${NC}"
echo -e "  WebSocket        : ${YELLOW}wss://${CF_RECORD_NAME}/ws/realtime${NC}"
echo -e "  Health check     : ${YELLOW}https://${CF_RECORD_NAME}/healthz${NC}"
echo -e "  Surgeon frontend : ${YELLOW}https://shalyamitra.quaasx108.com${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo ""
warn "When the slot ends, run: ./scripts/slot-stop.sh"
