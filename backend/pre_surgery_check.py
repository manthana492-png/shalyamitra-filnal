#!/usr/bin/env python3
"""
ShalyaMitra — Pre-Surgery System Check
═══════════════════════════════════════

Run this 30 minutes before surgery to verify all systems are operational.
Referenced in LIGHTNING_AI_DEPLOYMENT.md Step 10.

Usage:
    python pre_surgery_check.py

Requirements:
    pip install httpx grpcio  (already in requirements.txt)
"""

import asyncio
import sys
import time
import os

# Add parent directory to path so we can import app config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def run_checks():
    import httpx

    print("=" * 60)
    print("  ShalyaMitra — Pre-Surgery System Check")
    print("  " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    print()

    checks_passed = 0
    checks_failed = 0
    checks_warned = 0

    # ── 1. Environment Variables ──────────────────────────
    print("┌─ 1. Environment Variables")
    try:
        from app.config import settings

        if settings.nvidia_api_key:
            print(f"│  ✅ NVIDIA_API_KEY: {settings.nvidia_api_key[:12]}...{settings.nvidia_api_key[-4:]}")
            checks_passed += 1
        else:
            print("│  ❌ NVIDIA_API_KEY: NOT SET — get one at build.nvidia.com")
            checks_failed += 1

        if settings.openrouter_api_key:
            print(f"│  ✅ OPENROUTER_API_KEY: {settings.openrouter_api_key[:12]}...{settings.openrouter_api_key[-4:]}")
            checks_passed += 1
        else:
            print("│  ⚠️  OPENROUTER_API_KEY: NOT SET — fallback LLM unavailable")
            checks_warned += 1

        if settings.ngc_api_key:
            print(f"│  ✅ NGC_API_KEY: {settings.ngc_api_key[:12]}...{settings.ngc_api_key[-4:]}")
            checks_passed += 1
        else:
            print("│  ⚠️  NGC_API_KEY: NOT SET — Riva container pull may fail")
            checks_warned += 1

        print(f"│  ℹ️  GPU_PROVIDER: {settings.gpu_provider.value}")
        print(f"│  ℹ️  NIM_LIVE_TEST: {settings.nim_live_test}")
        print(f"│  ℹ️  Primary Model: {settings.nim_reasoning_model}")
        print(f"│  ℹ️  Vision Model: {settings.nim_vision_model}")
    except Exception as e:
        print(f"│  ❌ Config load failed: {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── 2. NIM API (Primary Inference) ────────────────────
    print("┌─ 2. NIM API — Nemotron 49B (Primary Inference)")
    try:
        from app.config import settings
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.post(
                f"{settings.nvidia_nim_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.nvidia_api_key}"},
                json={
                    "model": settings.nim_reasoning_model,
                    "messages": [{"role": "user", "content": "Respond with only: SYSTEM_CHECK_OK"}],
                    "max_tokens": 10,
                    "temperature": 0.0,
                },
            )
            if resp.status_code == 200:
                body = resp.json()
                reply = body["choices"][0]["message"]["content"].strip()
                print(f"│  ✅ NIM API: HTTP 200 — Model responded: \"{reply[:40]}\"")
                checks_passed += 1
            elif resp.status_code == 401:
                print(f"│  ❌ NIM API: HTTP 401 — Invalid NVIDIA_API_KEY")
                checks_failed += 1
            elif resp.status_code == 429:
                print(f"│  ⚠️  NIM API: HTTP 429 — Rate limited. Wait and retry.")
                checks_warned += 1
            else:
                print(f"│  ❌ NIM API: HTTP {resp.status_code} — {resp.text[:100]}")
                checks_failed += 1
    except Exception as e:
        print(f"│  ❌ NIM API: Connection failed — {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── 3. Backend Health ─────────────────────────────────
    print("┌─ 3. Backend API Health")
    try:
        async with httpx.AsyncClient(timeout=5.0) as http:
            resp = await http.get("http://localhost:8000/healthz")
            if resp.status_code == 200:
                data = resp.json()
                print(f"│  ✅ Backend: {data.get('service', '?')} v{data.get('version', '?')}")
                print(f"│     GPU Provider: {data.get('gpu_provider', '?')}")
                checks_passed += 1
            else:
                print(f"│  ❌ Backend: HTTP {resp.status_code}")
                checks_failed += 1
    except httpx.ConnectError:
        print("│  ❌ Backend: Not running on localhost:8000")
        print("│     Start with: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        checks_failed += 1
    except Exception as e:
        print(f"│  ❌ Backend: {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── 4. Agent Orchestrator ─────────────────────────────
    print("┌─ 4. Agent Orchestrator (11 Intelligence Pillars)")
    try:
        from app.agents.orchestrator import get_orchestrator
        orch = get_orchestrator()
        agent_count = len(orch.agents)
        if agent_count == 11:
            print(f"│  ✅ Agents: {agent_count}/11 pillars registered")
            for name, agent in orch.agents.items():
                print(f"│     • {agent.pillar}: {name}")
            checks_passed += 1
        else:
            print(f"│  ⚠️  Agents: {agent_count}/11 — some agents failed to register")
            checks_warned += 1
    except Exception as e:
        print(f"│  ❌ Orchestrator: {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── 5. PHI Redaction Engine ───────────────────────────
    print("┌─ 5. PHI Redaction Engine")
    try:
        from app.safety.phi_redaction import get_phi_engine
        engine = get_phi_engine()
        test_result = engine.redact("Patient Ravi Kumar, Aadhaar 1234 5678 9012, age 52")
        if test_result.phi_detected:
            print(f"│  ✅ PHI Engine: {len(test_result.matches)} entities detected and redacted")
            print(f"│     Categories: {test_result.categories_found}")
            print(f"│     Redacted: \"{test_result.redacted_text[:60]}...\"")
            checks_passed += 1
        else:
            print("│  ❌ PHI Engine: Failed to detect test PHI data")
            checks_failed += 1
    except Exception as e:
        print(f"│  ❌ PHI Engine: {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── 6. Clinical Guardrails ────────────────────────────
    print("┌─ 6. Clinical Guardrails Engine")
    try:
        from app.safety.clinical_guardrails import get_guardrails_engine
        engine = get_guardrails_engine()
        result = await engine.check("Give 200mg propofol now", agent_type="test", skip_llm=True)
        if result.outcome.value == "block":
            print(f"│  ✅ Guardrails: Correctly blocked unsafe dosing command")
            print(f"│     Violations: {[v.rule_name for v in result.violations]}")
            checks_passed += 1
        else:
            print(f"│  ⚠️  Guardrails: Outcome={result.outcome.value} (expected block)")
            checks_warned += 1
    except Exception as e:
        print(f"│  ❌ Guardrails: {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── 7. Privacy Router ─────────────────────────────────
    print("┌─ 7. Privacy Router (NIM Tier Routing)")
    try:
        from app.safety.privacy_router import get_privacy_router
        router = get_privacy_router()
        stats = router.get_stats()
        print(f"│  ✅ Privacy Router: Initialized")
        print(f"│     NIM configured: {stats['nvidia_nim_configured']}")
        print(f"│     OpenRouter configured: {stats['openrouter_configured']}")
        print(f"│     Models: {stats['models']['primary']}")
        checks_passed += 1
    except Exception as e:
        print(f"│  ❌ Privacy Router: {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── 8. Riva (ASR) ─────────────────────────────────────
    print("┌─ 8. NVIDIA Riva (Speech Recognition)")
    try:
        import grpc
        from app.config import settings
        channel = grpc.insecure_channel(settings.riva_grpc_url)
        # Quick connectivity check
        try:
            grpc.channel_ready_future(channel).result(timeout=3)
            print(f"│  ✅ Riva: Connected on {settings.riva_grpc_url}")
            checks_passed += 1
        except grpc.FutureTimeoutError:
            print(f"│  ⚠️  Riva: Not reachable on {settings.riva_grpc_url}")
            print("│     ASR will fall back to: Gemini Flash → Whisper → Browser Web Speech")
            checks_warned += 1
        finally:
            channel.close()
    except ImportError:
        print("│  ⚠️  Riva: grpcio not installed (pip install grpcio)")
        print("│     ASR will use browser-based fallback")
        checks_warned += 1
    except Exception as e:
        print(f"│  ⚠️  Riva: {e}")
        print("│     ASR will use fallback chain")
        checks_warned += 1
    print("└─")
    print()

    # ── 9. Marma Knowledge Base ───────────────────────────
    print("┌─ 9. Marma Knowledge Base")
    try:
        from app.knowledge.marma_db import get_marma_stats
        stats = get_marma_stats()
        print(f"│  ✅ Marma DB: {stats['total_points']} points ({stats['total_entries']} entries)")
        checks_passed += 1
    except Exception as e:
        print(f"│  ❌ Marma DB: {e}")
        checks_failed += 1
    print("└─")
    print()

    # ── Summary ───────────────────────────────────────────
    print()
    print("=" * 60)
    total = checks_passed + checks_failed + checks_warned
    if checks_failed == 0:
        print(f"  ✅ ALL CHECKS PASSED: {checks_passed}/{total} passed, {checks_warned} warnings")
        print()
        print("  🏥 System ready for surgery")
    else:
        print(f"  ❌ {checks_failed} CHECKS FAILED: {checks_passed} passed, {checks_warned} warnings")
        print()
        print("  ⚠️  Fix the failures above before proceeding")
    print("=" * 60)
    print()

    return checks_failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_checks())
    sys.exit(0 if success else 1)
