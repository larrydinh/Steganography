import numpy as np

from shared.stego.lsb import embed_lsb, extract_lsb
from shared.stego.dct import embed_dct, extract_dct
from shared.stego.dwt import embed_dwt, extract_dwt

from backend.app.services.crypto_service import build_secure_payload, recover_secure_payload


def embed_secret(image: np.ndarray, secret_text: str, password: str, method: str) -> np.ndarray:
    payload = build_secure_payload(secret_text, password)
    method = method.upper()

    if method == "LSB":
        return embed_lsb(image, payload)
    if method == "DCT":
        return embed_dct(image, payload)
    if method == "DWT":
        return embed_dwt(image, payload)

    raise ValueError(f"Unsupported method: {method}")


def extract_secret(image: np.ndarray, password: str, method: str) -> str:
    method = method.upper()

    if method == "LSB":
        payload = extract_lsb(image)
    elif method == "DCT":
        payload = extract_dct(image)
    elif method == "DWT":
        payload = extract_dwt(image)
    else:
        raise ValueError(f"Unsupported method: {method}")

    return recover_secure_payload(payload, password)