import numpy as np
import pywt
from PIL import Image

from shared.utils.bit_utils import (
    bytes_to_bits,
    bits_to_bytes,
    int_to_fixed_bytes,
    fixed_bytes_to_int,
)

HEADER_SIZE = 4


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image.astype(np.uint8)
    pil_img = Image.fromarray(image.astype(np.uint8))
    return np.array(pil_img.convert("L"), dtype=np.uint8)


def max_capacity_bits(image: np.ndarray) -> int:
    gray = _to_grayscale(image)
    coeffs2 = pywt.dwt2(gray.astype(np.float64), "haar")
    _, (lh, _, _) = coeffs2
    return lh.size


def embed_dwt(image: np.ndarray, payload: bytes) -> np.ndarray:
    gray = _to_grayscale(image).astype(np.float64)

    full_payload = int_to_fixed_bytes(len(payload), HEADER_SIZE) + payload
    bits = bytes_to_bits(full_payload)

    coeffs2 = pywt.dwt2(gray, "haar")
    ll, (lh, hl, hh) = coeffs2

    flat_lh = lh.flatten().copy()
    if len(bits) > flat_lh.size:
        raise ValueError("Payload too large for DWT image capacity.")

    for i, bit in enumerate(bits):
        coeff = int(round(flat_lh[i]))
        if bit == 1:
            if coeff % 2 == 0:
                coeff += 1
        else:
            if coeff % 2 != 0:
                coeff += 1
        flat_lh[i] = coeff

    lh_embedded = flat_lh.reshape(lh.shape)
    reconstructed = pywt.idwt2((ll, (lh_embedded, hl, hh)), "haar")
    reconstructed = np.clip(reconstructed, 0, 255).astype(np.uint8)

    return np.stack([reconstructed] * 3, axis=2)


def extract_dwt(image: np.ndarray) -> bytes:
    gray = _to_grayscale(image).astype(np.float64)

    coeffs2 = pywt.dwt2(gray, "haar")
    _, (lh, _, _) = coeffs2

    bits = []
    target_bits = None

    for coeff in lh.flatten():
        value = int(round(coeff))
        bits.append(abs(value) % 2)

        if target_bits is None and len(bits) >= HEADER_SIZE * 8:
            header = bits_to_bytes(bits[: HEADER_SIZE * 8])
            payload_length = fixed_bytes_to_int(header)
            target_bits = (HEADER_SIZE + payload_length) * 8

        if target_bits is not None and len(bits) >= target_bits:
            break

    if target_bits is None:
        raise ValueError("Could not read DWT payload header.")

    data = bits_to_bytes(bits[:target_bits])
    return data[HEADER_SIZE:]