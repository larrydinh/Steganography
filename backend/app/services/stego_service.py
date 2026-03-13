import numpy as np

from shared.stego.lsb import embed_lsb, extract_lsb
from backend.app.services.crypto_service import build_secure_payload, recover_secure_payload


def embed_secret(image: np.ndarray, secret_text: str, password: str, method: str) -> np.ndarray:
    payload = build_secure_payload(secret_text, password)

    if method.upper() == "LSB":
        return embed_lsb(image, payload)

    raise ValueError(f"Unsupported method: {method}")


def extract_secret(image: np.ndarray, password: str, method: str) -> str:
    if method.upper() == "LSB":
        payload = extract_lsb(image)
    else:
        raise ValueError(f"Unsupported method: {method}")

    return recover_secure_payload(payload, password)