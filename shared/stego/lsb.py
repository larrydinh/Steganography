import numpy as np

from shared.utils.bit_utils import (
    bytes_to_bits,
    bits_to_bytes,
    int_to_fixed_bytes,
    fixed_bytes_to_int,
)

HEADER_SIZE = 4  # bytes


def validate_image(image: np.ndarray) -> None:
    if image.dtype != np.uint8:
        raise ValueError("Image must be uint8.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Image must be RGB with 3 channels.")


def max_capacity_bits(image: np.ndarray) -> int:
    h, w, c = image.shape
    return h * w * c


def embed_lsb(image: np.ndarray, payload: bytes) -> np.ndarray:
    validate_image(image)

    full_payload = int_to_fixed_bytes(len(payload), HEADER_SIZE) + payload
    bits = bytes_to_bits(full_payload)

    if len(bits) > max_capacity_bits(image):
        raise ValueError("Payload too large for selected image.")

    flat = image.flatten().copy()
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | bit

    return flat.reshape(image.shape)


def extract_lsb(image: np.ndarray) -> bytes:
    validate_image(image)
    flat = image.flatten()

    header_bits = [flat[i] & 1 for i in range(HEADER_SIZE * 8)]
    header_bytes = bits_to_bytes(header_bits)
    payload_length = fixed_bytes_to_int(header_bytes)

    total_bits = (HEADER_SIZE + payload_length) * 8
    if total_bits > len(flat):
        raise ValueError("Invalid or corrupted stego image.")

    all_bits = [flat[i] & 1 for i in range(total_bits)]
    all_bytes = bits_to_bytes(all_bits)

    return all_bytes[HEADER_SIZE:]