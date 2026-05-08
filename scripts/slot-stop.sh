#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
# slot-stop.sh — Deactivate a ShalyaMitra surgery slot
# ══════════════════════════════════════════════════════════
# Run this after the surgery slot ends to:
#   1. Gracefully stop Docker Compose stack
#   2. Remove / null-route Cloudflare DNS record
#   3. Confirm shutdown
#
# Same env vars required as slot-start.sh
# ══════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { echo -e "${CYAN}[slot-stop]${NC} $*"; }
ok()   { echo -e "${GREEN}[slot-stop]${NC} $*"; }
warn() { echo -e "${YELLOW}[slot-stop]${NC} $*"; }

CF_API_TOKEN="${CF_API_TOKEN:-}"
CF_ZONE_ID="${CF_ZONE_ID:-}"
CF_RECORD_NAME="${CF_RECORD_NAME:-gpu.shalyamitra.quaasx108.com}"
GPU_STACK_DIR="${GPU_STACK_DIR:-$(dirname "$0")/../gpu-stack}"

# ── 1. Stop Docker Compose ────────────────────────────────
log "Stopping GPU stack..."
cd "$GPU_STACK_DIR"
docker compose -f docker-compose.gpu.yml down --remove-orphans
ok "GPU stack stopped."

# ── 2. Remove Cloudflare DNS record ───────────────────────
if [[ -z "$CF_API_TOKEN" || -z "$CF_ZONE_ID" ]]; then
    warn "CF_API_TOKEN or CF_ZONE_ID not set — skipping Cloudflare DNS cleanup."
    warn "Manually remove the gpu.shalyamitra.quaasx108.com A record from Cloudflare."
else
    log "Removing Cloudflare DNS record for ${CF_RECORD_NAME}..."
    RECORD_RESPONSE=$(curl -sf -X GET \
        "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records?type=A&name=${CF_RECORD_NAME}" \
        -H "Authorization: Bearer ${CF_API_TOKEN}" \
        -H "Content-Type: application/json")

    RECORD_ID=$(echo "$RECORD_RESPONSE" | python3 -c "import sys,json; recs=json.load(sys.stdin)['result']; print(recs[0]['id'] if recs else '')" 2>/dev/null || true)

    if [[ -n "$RECORD_ID" ]]; then
        curl -sf -X DELETE \
            "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records/${RECORD_ID}" \
            -H "Authorization: Bearer ${CF_API_TOKEN}" > /dev/null
        ok "DNS record removed. gpu.shalyamitra.quaasx108.com is now offline."
    else
        warn "No DNS record found for ${CF_RECORD_NAME} — already removed."
    fi
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ShalyaMitra slot is OFFLINE                ${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "  GPU cost stopped. No idle billing."
echo -e "  Frontend (Vercel) still accessible for surgeons."
echo -e "  Auth (Supabase) still accessible for post-op review."
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
