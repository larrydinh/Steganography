from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from backend.app.services.detection.scoring import (
    band_from_score,
    combine_scores,
    consistency_suspicion,
    entropy_suspicion,
    lsb_balance_suspicion,
)


CHANNEL_NAMES = ["R", "G", "B"]


def _to_rgb_array(image: Image.Image) -> np.ndarray:
    rgb_image = image.convert("RGB")
    return np.array(rgb_image)


def _lsb_plane(channel: np.ndarray) -> np.ndarray:
    return channel & 1


def _binary_entropy(bits: np.ndarray) -> float:
    p1 = float(bits.mean())
    p0 = 1.0 - p1
    eps = 1e-12
    return float(-(p0 * np.log2(p0 + eps) + p1 * np.log2(p1 + eps)))


def _balance_status(balance: float) -> str:
    if 0.49 <= balance <= 0.51:
        return "suspicious"
    if 0.47 <= balance <= 0.53:
        return "warning"
    return "normal"


def _entropy_status(entropy_value: float) -> str:
    if entropy_value >= 0.995:
        return "suspicious"
    if entropy_value >= 0.98:
        return "warning"
    return "normal"


def run_heuristic_lsb(
    image: Image.Image,
    filename: str,
    target: str = "lsb",
) -> dict[str, Any]:
    """
    First-pass heuristic spatial-domain LSB detector.
    Returns a response matching DetectionResponse schema.
    """
    rgb = _to_rgb_array(image)
    height, width, _ = rgb.shape
    image_type = (image.format or "UNKNOWN").upper()

    signals: list[dict[str, Any]] = []
    balances: list[float] = []
    entropies: list[float] = []

    for i, ch_name in enumerate(CHANNEL_NAMES):
        channel = rgb[:, :, i]
        bits = _lsb_plane(channel)

        balance = float(bits.mean())
        entropy_value = _binary_entropy(bits)

        balances.append(balance)
        entropies.append(entropy_value)

        signals.append(
            {
                "name": f"{ch_name}_lsb_balance",
                "value": round(balance, 6),
                "status": _balance_status(balance),
                "explanation": (
                    "A near 50/50 distribution of least-significant bits can be "
                    "consistent with randomized LSB embedding."
                ),
            }
        )

        signals.append(
            {
                "name": f"{ch_name}_lsb_entropy",
                "value": round(entropy_value, 6),
                "status": _entropy_status(entropy_value),
                "explanation": (
                    "Very high entropy in the least-significant bit-plane can be "
                    "suspicious for hidden-data embedding."
                ),
            }
        )

    balance_scores = [lsb_balance_suspicion(b) for b in balances]
    entropy_scores = [entropy_suspicion(e) for e in entropies]
    consistency_score = consistency_suspicion(balances)

    risk_score = combine_scores(
        balance_scores=balance_scores,
        entropy_scores=entropy_scores,
        consistency_score=consistency_score,
    )
    risk_band = band_from_score(risk_score)

    consistency_spread = round(max(balances) - min(balances), 6)
    signals.append(
        {
            "name": "channel_balance_consistency",
            "value": consistency_spread,
            "status": "warning" if consistency_spread < 0.02 else "normal",
            "explanation": (
                "Very similar LSB balance across all RGB channels can be a mild "
                "indicator of systematic embedding."
            ),
        }
    )

    format_warning = None
    notes = [
        "This detector is heuristic-based and intended for first-pass screening.",
        "A high score means suspicious statistical patterns, not proof of hidden content.",
    ]

    if image_type in {"JPG", "JPEG"}:
        format_warning = (
            "JPEG images are less reliable for simple spatial LSB analysis. "
            "A JPEG/DCT-specific detector is recommended for stronger results."
        )
        notes.append("Result confidence is lower for JPEG under spatial LSB heuristics.")

    return {
        "filename": filename,
        "image_type": image_type,
        "width": width,
        "height": height,
        "detector_used": "heuristic_lsb_v1",
        "target": target,
        "risk_score": risk_score,
        "risk_band": risk_band,
        "confidence_note": "Statistical risk score, not proof of hidden content.",
        "signals": signals,
        "technical": {
            "channels_analyzed": CHANNEL_NAMES,
            "format_warning": format_warning,
            "notes": notes,
        },
    }