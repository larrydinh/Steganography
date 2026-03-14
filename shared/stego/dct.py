import numpy as np
from PIL import Image

from shared.utils.bit_utils import (
    bytes_to_bits,
    bits_to_bytes,
    int_to_fixed_bytes,
    fixed_bytes_to_int,
)

HEADER_SIZE = 4
BLOCK_SIZE = 8
COEFF_POS = (4, 3)


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image.astype(np.uint8)
    pil_img = Image.fromarray(image.astype(np.uint8))
    return np.array(pil_img.convert("L"), dtype=np.uint8)


def _dct2(block: np.ndarray) -> np.ndarray:
    block = block.astype(np.float64)
    n = block.shape[0]
    result = np.zeros((n, n), dtype=np.float64)

    for u in range(n):
        for v in range(n):
            alpha_u = np.sqrt(1 / n) if u == 0 else np.sqrt(2 / n)
            alpha_v = np.sqrt(1 / n) if v == 0 else np.sqrt(2 / n)

            s = 0.0
            for x in range(n):
                for y in range(n):
                    s += (
                        block[x, y]
                        * np.cos(((2 * x + 1) * u * np.pi) / (2 * n))
                        * np.cos(((2 * y + 1) * v * np.pi) / (2 * n))
                    )
            result[u, v] = alpha_u * alpha_v * s

    return result


def _idct2(block: np.ndarray) -> np.ndarray:
    block = block.astype(np.float64)
    n = block.shape[0]
    result = np.zeros((n, n), dtype=np.float64)

    for x in range(n):
        for y in range(n):
            s = 0.0
            for u in range(n):
                for v in range(n):
                    alpha_u = np.sqrt(1 / n) if u == 0 else np.sqrt(2 / n)
                    alpha_v = np.sqrt(1 / n) if v == 0 else np.sqrt(2 / n)
                    s += (
                        alpha_u
                        * alpha_v
                        * block[u, v]
                        * np.cos(((2 * x + 1) * u * np.pi) / (2 * n))
                        * np.cos(((2 * y + 1) * v * np.pi) / (2 * n))
                    )
            result[x, y] = s

    return result


def _iter_blocks(img: np.ndarray, block_size: int = BLOCK_SIZE):
    h, w = img.shape
    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            yield y, x, img[y:y + block_size, x:x + block_size]


def max_capacity_bits(image: np.ndarray) -> int:
    gray = _to_grayscale(image)
    h, w = gray.shape
    return (h // BLOCK_SIZE) * (w // BLOCK_SIZE)


def embed_dct(image: np.ndarray, payload: bytes) -> np.ndarray:
    gray = _to_grayscale(image)
    output = gray.astype(np.float64).copy()

    full_payload = int_to_fixed_bytes(len(payload), HEADER_SIZE) + payload
    bits = bytes_to_bits(full_payload)

    capacity = max_capacity_bits(gray)
    if len(bits) > capacity:
        raise ValueError("Payload too large for DCT image capacity.")

    blocks = list(_iter_blocks(output))

    for i, bit in enumerate(bits):
        y, x, block = blocks[i]
        centered = block - 128.0
        dct_block = _dct2(centered)

        r, c = COEFF_POS
        coeff = int(round(dct_block[r, c]))

        if bit == 1:
            if coeff % 2 == 0:
                coeff += 1
        else:
            if coeff % 2 != 0:
                coeff += 1

        dct_block[r, c] = coeff

        restored = _idct2(dct_block) + 128.0
        output[y:y + BLOCK_SIZE, x:x + BLOCK_SIZE] = restored

    output = np.clip(output, 0, 255).astype(np.uint8)
    return np.stack([output] * 3, axis=2)


def extract_dct(image: np.ndarray) -> bytes:
    gray = _to_grayscale(image)
    bits = []
    target_bits = None

    for _, _, block in _iter_blocks(gray.astype(np.float64)):
        centered = block - 128.0
        dct_block = _dct2(centered)

        r, c = COEFF_POS
        coeff = int(round(dct_block[r, c]))
        bits.append(abs(coeff) % 2)

        if target_bits is None and len(bits) >= HEADER_SIZE * 8:
            header = bits_to_bytes(bits[: HEADER_SIZE * 8])
            payload_length = fixed_bytes_to_int(header)
            target_bits = (HEADER_SIZE + payload_length) * 8

        if target_bits is not None and len(bits) >= target_bits:
            break

    if target_bits is None:
        raise ValueError("Could not read DCT payload header.")

    data = bits_to_bytes(bits[:target_bits])
    return data[HEADER_SIZE:]