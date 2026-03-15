from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image


MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "stego_cnn_lsb.pt"


def run_cnn_detector(
    image: Image.Image,
    filename: str,
    target: str = "lsb",
) -> dict[str, Any]:
    """
    Placeholder for future CNN inference.

    Replace this with real torch model loading + preprocessing later.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"CNN model file not found at: {MODEL_PATH}"
        )

    raise NotImplementedError(
        "CNN detector hook exists, but inference is not implemented yet."
    )