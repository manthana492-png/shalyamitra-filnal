# ShalyaMitra — Phase 2 Clinical Hardening Checklist

Operational checklist before hospital pilots. This complements Phase 1 “real product baseline” delivery.

## 1. Failure modes & degradation matrix

| Subsystem | Fail-open vs fail-safe | Default timeout | Degraded behaviour |
|-----------|------------------------|-----------------|-------------------|
| Vision (Holoscan) | Fail-safe — never invent anatomy | 5s ingest RTT | Switch to VLM fallback + log drop rate |
| Vision (cloud VLM) | Fail-safe — conservative wording | 15s | Skip cycle; surface “vision unavailable” once |
| ASR (Riva → cloud) | Fail-open listen path | 8–10s | Browser ASR / silence |
| TTS (Piper → Fish → cloud) | Fail-open speech | 2s critical | Browser speech synthesis flag |
| ShalyaBus / WS | Fail-safe alert mirroring | ping 30s | reconnect + chronicle gap marker |

Document **per-site** overrides in `ARCHITECTURE.md` deployment notes.

## 2. Model validation & calibration

- Maintain **versioned** datasets for haemorrhage, instrument count, phase detection.
- Emit alerts only when \(confidence ≥ calibrated threshold\) **and** secondary sanity checks pass (temporal consistency, phase appropriateness).
- Regression harness on every model artefact update (latency + confusion matrices + worst-case review).

## 3. Audit traceability

- Every **DISPLAY_ALERT** / mirrored **ALERT** must carry `session_id`, monotonic `at`, `source`, and correlation id when crossing Holoscan-bridge ↔ agent.
- Chronicler must summarize AI prompts/responses with PHI redaction already applied (PrivacyRouter).

## 4. Security & compliance

- Rotate `INTERNAL_BUS_TOKEN`, LiveKit keys, and Supabase service keys on a fixed schedule.
- mTLS or signed JWT between holoscan-bridge ↔ agent in production networks.
- PHI redaction QA on noisy transcripts (MRNs embedded in speech, dictation habits).

## 5. Runbooks

- **Rollback**: pinned container digests + compose profile switch to `demo` GPU provider for theatre-only UI rehearsal.
- **Incident**: preserve `/api/ops/metrics/summary` snapshots + WS reconnect counts.

## 6. Governance sign-off

- Clinical safety officer reviews alert wording + audio prompts.
- Anaesthesia lead signs off monitor sentinel thresholds per specialty bundle.
