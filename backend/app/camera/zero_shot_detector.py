"""
ShalyaMitra — Zero-Shot Instrument Detector

Replaces YOLOv11 entirely. No dataset, no training, no fine-tuning needed.
Uses a 3-tier cascade of pre-trained open-set models:

  Tier 1: Grounding DINO 1.5 Pro (DeepDataSpace API)
           — best accuracy, dedicated zero-shot detector
           — trained on 20M image-text pairs
           — handles any surgical instrument text prompt

  Tier 2: Microsoft Florence-2 (HuggingFace local / Replicate API)
           — open-source, MIT license, runs on CPU or GPU
           — prompt: "<CAPTION_TO_PHRASE_GROUNDING>"
           — returns bounding boxes + labels

  Tier 3: Gemini 2.0 Flash Vision (already in your VLM cascade)
           — already integrated, acts as final fallback
           — returns counts + positions as JSON

All three return a unified InstrumentDetection list so the
Sentinel Agent receives the same format regardless of tier used.
"""

from __future__ import annotations
import base64, asyncio, time, json
from dataclasses import dataclass
from typing import Any, Optional
import httpx
from app.config import settings

# ─── Canonical instrument list for the OR ───────────────
SURGICAL_INSTRUMENTS = [
    "scalpel", "forceps", "scissors", "retractor",
    "needle holder", "suction device", "cautery",
    "clamp", "clip applier", "trocar", "stapler",
    "laparoscope", "irrigator", "drain", "sponge",
    "swab", "gauze", "surgical needle", "suture",
    "haemostat", "dissector", "dilator",
]

INSTRUMENT_PROMPT = " . ".join(SURGICAL_INSTRUMENTS)


@dataclass
class InstrumentDetection:
    name: str
    confidence: float
    bbox: Optional[list[float]]   # [x1, y1, x2, y2] normalised 0-1
    count: int = 1
    source: str = "unknown"


@dataclass
class DetectionResult:
    instruments: list[InstrumentDetection]
    total_count: int
    source_tier: int        # 1=GDINO, 2=Florence, 3=Gemini
    source_name: str
    latency_ms: float
    raw: dict[str, Any]


# ════════════════════════════════════════════════════════
# Tier 1 — Grounding DINO 1.5 (DeepDataSpace API)
# ════════════════════════════════════════════════════════

class GroundingDINODetector:
    """
    Grounding DINO 1.5 Pro via the DeepDataSpace API.
    Requires: GROUNDING_DINO_API_TOKEN in .env

    Get token: https://deepdataspace.com  (apply for API access)
    GitHub:    https://github.com/IDEA-Research/Grounding-DINO-1.5-API
    """

    BASE_URL = "https://api.deepdataspace.com"

    def __init__(self):
        self._token = getattr(settings, "grounding_dino_api_token", "")
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=15.0)
        return self._http

    async def detect(self, image_b64: str) -> Optional[DetectionResult]:
        if not self._token:
            return None
        try:
            t0 = time.time()
            http = await self._get_http()
            resp = await http.post(
                f"{self.BASE_URL}/v2/task/grounding_dino/detection",
                headers={
                    "Authorization": f"Token {self._token}",
                    "Content-Type": "application/json",
                },
                json={
                    "image": image_b64,
                    "targets": INSTRUMENT_PROMPT,
                    "model": "GroundingDINO-1.5-Pro",
                    "threshold": 0.35,
                },
                timeout=12.0,
            )
            latency = (time.time() - t0) * 1000

            if resp.status_code != 200:
                return None

            data = resp.json()
            objects = data.get("data", {}).get("objects", [])

            detections = []
            for obj in objects:
                detections.append(InstrumentDetection(
                    name=obj.get("category", "unknown"),
                    confidence=float(obj.get("score", 0)),
                    bbox=obj.get("bbox"),        # [x1,y1,x2,y2]
                    source="grounding_dino_1.5",
                ))

            return DetectionResult(
                instruments=detections,
                total_count=len(detections),
                source_tier=1,
                source_name="Grounding DINO 1.5 Pro",
                latency_ms=latency,
                raw=data,
            )
        except Exception as e:
            print(f"[GDINO] Error: {e}")
            return None


# ════════════════════════════════════════════════════════
# Tier 2 — Microsoft Florence-2 (HuggingFace local)
# ════════════════════════════════════════════════════════

class Florence2Detector:
    """
    Microsoft Florence-2 — open-source, MIT licence, zero-shot.
    Runs locally on CPU (slow) or GPU (fast).
    Model: microsoft/Florence-2-large  (~1.5GB download, once)

    No API key. No training. No cost.
    HuggingFace: https://huggingface.co/microsoft/Florence-2-large
    """

    MODEL_ID = "microsoft/Florence-2-large"
    _model = None
    _processor = None
    _loaded = False

    async def _load_model(self):
        """Load Florence-2 model (lazy, once per process)."""
        if self._loaded:
            return
        try:
            # Run heavy import in thread to avoid blocking event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_sync)
        except Exception as e:
            print(f"[Florence2] Load error: {e}")

    def _load_sync(self):
        import torch
        from transformers import AutoProcessor, AutoModelForCausalLM

        device = "cuda" if __import__("torch").cuda.is_available() else "cpu"
        dtype = __import__("torch").float16 if device == "cuda" else __import__("torch").float32

        Florence2Detector._processor = AutoProcessor.from_pretrained(
            self.MODEL_ID, trust_remote_code=True
        )
        Florence2Detector._model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_ID,
            torch_dtype=dtype,
            trust_remote_code=True,
        ).to(device)
        Florence2Detector._loaded = True
        print(f"[Florence2] Model loaded on {device}")

    async def detect(self, image_b64: str) -> Optional[DetectionResult]:
        await self._load_model()
        if not self._loaded:
            return None

        try:
            t0 = time.time()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._detect_sync, image_b64
            )
            latency = (time.time() - t0) * 1000

            if result is None:
                return None

            detections = []
            # Florence-2 returns labels + bboxes
            labels = result.get("labels", [])
            bboxes = result.get("bboxes", [])

            for label, bbox in zip(labels, bboxes):
                # Filter to surgical instruments only
                label_lower = label.lower()
                if any(inst in label_lower for inst in SURGICAL_INSTRUMENTS):
                    detections.append(InstrumentDetection(
                        name=label,
                        confidence=0.85,    # Florence-2 doesn't return scores
                        bbox=bbox,
                        source="florence2",
                    ))

            return DetectionResult(
                instruments=detections,
                total_count=len(detections),
                source_tier=2,
                source_name="Florence-2 Large",
                latency_ms=latency,
                raw=result,
            )
        except Exception as e:
            print(f"[Florence2] Detection error: {e}")
            return None

    def _detect_sync(self, image_b64: str) -> Optional[dict]:
        import io
        from PIL import Image

        # Decode image
        img_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        device = "cuda" if __import__("torch").cuda.is_available() else "cpu"

        # Use grounded detection with instrument prompt
        task = "<CAPTION_TO_PHRASE_GROUNDING>"
        text_prompt = (
            "A surgical tray with "
            + ", ".join(SURGICAL_INSTRUMENTS[:10])
            + " on it."
        )

        inputs = self._processor(
            text=text_prompt, images=image, return_tensors="pt"
        ).to(device)

        generated_ids = self._model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=512,
            num_beams=3,
        )

        generated_text = self._processor.batch_decode(
            generated_ids, skip_special_tokens=False
        )[0]

        parsed = self._processor.post_process_generation(
            generated_text,
            task=task,
            image_size=(image.width, image.height),
        )

        result = parsed.get(task, {})

        # Normalise bboxes to 0-1
        w, h = image.width, image.height
        norm_bboxes = []
        for bbox in result.get("bboxes", []):
            norm_bboxes.append([
                bbox[0] / w, bbox[1] / h,
                bbox[2] / w, bbox[3] / h,
            ])
        result["bboxes"] = norm_bboxes

        return result


# ════════════════════════════════════════════════════════
# Tier 3 — Gemini / OpenRouter VLM (already integrated)
# ════════════════════════════════════════════════════════

class GeminiInstrumentDetector:
    """
    Gemini 2.0 Flash Vision via OpenRouter.
    Already in VisionFallbackPipeline — this wraps it specifically
    for instrument counting/detection in a structured JSON format.
    """

    async def detect(self, image_b64: str) -> Optional[DetectionResult]:
        if not getattr(settings, "openrouter_api_key", ""):
            return None

        prompt = """You are a surgical instrument detection system.
Analyse this image of a surgical instrument tray.
Return ONLY a JSON object:
{
  "instruments": [
    {"name": "forceps", "count": 2, "confidence": 0.95},
    {"name": "scalpel", "count": 1, "confidence": 0.90}
  ],
  "total_count": 3,
  "swabs": 4,
  "needles": 2,
  "notes": "Any notable observations"
}
Be precise. Only list items you can clearly see."""

        try:
            t0 = time.time()
            async with httpx.AsyncClient(timeout=12.0) as http:
                resp = await http.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "HTTP-Referer": "https://shalyamitra.dev",
                        "X-Title": "ShalyaMitra Instrument Detection",
                    },
                    json={
                        "model": "google/gemini-2.0-flash-001",
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }},
                            ],
                        }],
                        "max_tokens": 400,
                        "temperature": 0.1,
                        "response_format": {"type": "json_object"},
                    },
                )
            latency = (time.time() - t0) * 1000

            if resp.status_code != 200:
                return None

            content = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(content)

            detections = []
            for inst in data.get("instruments", []):
                detections.append(InstrumentDetection(
                    name=inst.get("name", "unknown"),
                    confidence=float(inst.get("confidence", 0.8)),
                    bbox=None,          # Gemini doesn't return bboxes
                    count=int(inst.get("count", 1)),
                    source="gemini_flash",
                ))

            return DetectionResult(
                instruments=detections,
                total_count=data.get("total_count", len(detections)),
                source_tier=3,
                source_name="Gemini 2.0 Flash Vision",
                latency_ms=latency,
                raw=data,
            )
        except Exception as e:
            print(f"[GeminiDetect] Error: {e}")
            return None


# ════════════════════════════════════════════════════════
# Master Zero-Shot Detector (orchestrates all 3 tiers)
# ════════════════════════════════════════════════════════

class ZeroShotInstrumentDetector:
    """
    Production-ready zero-shot surgical instrument detector.

    No training. No dataset. No fine-tuning.

    Usage:
        detector = ZeroShotInstrumentDetector()
        result = await detector.detect(image_b64)
        print(result.instruments)   # List[InstrumentDetection]
        print(result.total_count)
        print(result.source_name)   # Which tier was used
    """

    def __init__(self):
        self._gdino = GroundingDINODetector()
        self._florence = Florence2Detector()
        self._gemini = GeminiInstrumentDetector()

    async def detect(self, image_b64: str) -> DetectionResult:
        """
        Detect surgical instruments using zero-shot cascade.
        Tries Tier 1 first; falls back automatically.
        """

        # Tier 1: Grounding DINO 1.5 (best accuracy + bboxes)
        result = await self._gdino.detect(image_b64)
        if result and result.total_count >= 0:
            print(f"[ZeroShot] Tier 1 (GDINO): {result.total_count} instruments, "
                  f"{result.latency_ms:.0f}ms")
            return result

        # Tier 2: Florence-2 (local, free, MIT licence)
        result = await self._florence.detect(image_b64)
        if result and result.total_count >= 0:
            print(f"[ZeroShot] Tier 2 (Florence2): {result.total_count} instruments, "
                  f"{result.latency_ms:.0f}ms")
            return result

        # Tier 3: Gemini Flash (already have the key)
        result = await self._gemini.detect(image_b64)
        if result:
            print(f"[ZeroShot] Tier 3 (Gemini): {result.total_count} instruments, "
                  f"{result.latency_ms:.0f}ms")
            return result

        # All tiers failed — return empty result
        return DetectionResult(
            instruments=[],
            total_count=0,
            source_tier=0,
            source_name="all_failed",
            latency_ms=0,
            raw={},
        )

    async def detect_with_count_diff(
        self,
        image_b64: str,
        baseline: dict[str, int],
    ) -> tuple[DetectionResult, list[str]]:
        """
        Detect instruments AND compare against baseline count.
        Returns (result, list_of_discrepancies).

        baseline = {"forceps": 2, "scalpel": 1, ...}
        """
        result = await self.detect(image_b64)

        current_counts: dict[str, int] = {}
        for det in result.instruments:
            current_counts[det.name.lower()] = (
                current_counts.get(det.name.lower(), 0) + det.count
            )

        discrepancies = []
        for instrument, expected in baseline.items():
            actual = current_counts.get(instrument.lower(), 0)
            if actual < expected:
                diff = expected - actual
                discrepancies.append(
                    f"{instrument}: {diff} MISSING (expected {expected}, found {actual})"
                )

        return result, discrepancies


# Singleton
_detector: Optional[ZeroShotInstrumentDetector] = None


def get_instrument_detector() -> ZeroShotInstrumentDetector:
    global _detector
    if _detector is None:
        _detector = ZeroShotInstrumentDetector()
    return _detector
