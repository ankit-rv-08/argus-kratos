"""Local Kratos inference shared by the CLI and Argus SSE endpoint."""

from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

MODEL_PATH = Path(__file__).parent / "llama-3.2-1b-instruct.Q4_K_M.gguf"

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover
    Llama = None


@lru_cache(maxsize=1)
def load_model() -> Any:
    if Llama is None or not MODEL_PATH.is_file():
        return None
    return Llama(model_path=str(MODEL_PATH), n_gpu_layers=-1, n_ctx=2048, verbose=False)


def _parse_model_output(raw_text: str) -> dict[str, Any]:
    """Parse model output without masking invalid classifications."""
    try:
        parsed = json.loads(raw_text)
        parsed.setdefault("ticker", "NVDA")
        parsed.setdefault("sentiment", "Neutral")
        parsed.setdefault("risk_factor", raw_text.strip())
        return parsed
    except json.JSONDecodeError:
        pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(raw_text[start : end + 1])
            parsed.setdefault("ticker", "NVDA")
            parsed.setdefault("sentiment", "Neutral")
            parsed.setdefault("risk_factor", raw_text.replace("<|im_tag|>", "").strip())
            return parsed
        except json.JSONDecodeError:
            pass

    return {
        "ticker": "NVDA",
        "sentiment": "Unparseable",
        "risk_factor": f"Model did not return valid JSON: {raw_text[:120]!r}",
        "parse_error": True,
    }


def analyze_context(context: str) -> dict[str, Any]:
    model = load_model()
    if model is None:
        return {
            "ticker": "NVDA",
            "sentiment": "Bullish",
            "risk_factor": "Export restrictions may pressure APAC growth.",
            "engine": "fallback",
            "tokens": 0,
            "elapsed": 0.0,
        }
    prompt = f"""<|im_start|>system
You are Kratos, an expert quantitative financial analyst. Analyze the context and extract sentiment. Respond ONLY with a valid JSON object: {{\"ticker\": \"NVDA\", \"sentiment\": \"Bullish\"|\"Bearish\"|\"Neutral\", \"risk_factor\": \"<summary>\"}}<|im_end|>
<|im_start|>user
Context:
{context}<|im_end|>
<|im_start|>assistant
"""
    started = time.perf_counter()
    result = model(prompt, max_tokens=60, temperature=0.1, stop=["<|im_end|>"])
    elapsed = time.perf_counter() - started
    raw_text = result["choices"][0]["text"].strip()
    parsed = _parse_model_output(raw_text)
    usage = result.get("usage", {})
    parsed.update({"engine": "llama.cpp / Apple Metal", "tokens": usage.get("completion_tokens", 0), "elapsed": elapsed})
    return parsed
