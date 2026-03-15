from __future__ import annotations

from typing import Any

from PIL import Image

from backend.app.services.detection.cnn_inference import run_cnn_detector
from backend.app.services.detection.heuristic_lsb import run_heuristic_lsb


VALID_MODES = {"auto", "heuristic", "cnn"}
VALID_TARGETS = {"auto", "lsb", "dct"}


def analyze_image(
    image: Image.Image,
    filename: str,
    mode: str = "auto",
    target: str = "auto",
    explain: bool = True,
) -> dict[str, Any]:
    """
    Route the image to the most appropriate detector.
    """
    del explain  # reserved for future richer explanations

    mode = (mode or "auto").lower()
    target = (target or "auto").lower()
    image_type = (image.format or "").upper()

    if mode not in VALID_MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if target not in VALID_TARGETS:
        raise ValueError(f"Unsupported target: {target}")

    if mode == "heuristic":
        chosen_target = "lsb" if target == "auto" else target
        return run_heuristic_lsb(image=image, filename=filename, target=chosen_target)

    if mode == "cnn":
        chosen_target = "lsb" if target == "auto" else target
        return run_cnn_detector(image=image, filename=filename, target=chosen_target)

    # auto mode
    if image_type in {"PNG", "BMP", "TIFF"}:
        return run_heuristic_lsb(image=image, filename=filename, target="lsb")

    if image_type in {"JPG", "JPEG"}:
        # For now, still use heuristic LSB with warning in response.
        return run_heuristic_lsb(image=image, filename=filename, target="lsb")

    # fallback
    chosen_target = "lsb" if target == "auto" else target
    return run_heuristic_lsb(image=image, filename=filename, target=chosen_target)