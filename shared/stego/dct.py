import numpy as np

from shared.utils.bit_utils import (
    bytes_to_bits,
    bits_to_bytes,
    int_to_fixed_bytes,
    fixed_bytes_to_int,
)

HEADER_SIZE = 4
BLOCK_SIZE = 8
COEFF_POS = (4, 3)
QUANT_STEP = 16.0
EMBED_CHANNEL = 2  # RGB image: 0=Red, 1=Green, 2=Blue


def _validate_rgb_image(image: np.ndarray) -> None:
    if image.dtype != np.uint8:
        raise ValueError("Image must be uint8.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Image must be RGB with 3 channels.")


def _get_embedding_channel(image: np.ndarray) -> np.ndarray:
    """
    DCT should not convert the whole image to grayscale.
    Instead, embed only in one RGB channel and keep the other channels unchanged.
    This preserves the color of the encoded image.
    """
    _validate_rgb_image(image)
    return image[:, :, EMBED_CHANNEL]


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


def _iter_blocks(channel: np.ndarray, block_size: int = BLOCK_SIZE):
    h, w = channel.shape
    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            yield y, x, channel[y:y + block_size, x:x + block_size]


def max_capacity_bits(image: np.ndarray) -> int:
    channel = _get_embedding_channel(image)
    h, w = channel.shape
    return (h // BLOCK_SIZE) * (w // BLOCK_SIZE)


def embed_dct(image: np.ndarray, payload: bytes) -> np.ndarray:
    _validate_rgb_image(image)

    # Keep the original RGB image. Only modify one channel.
    output_image = image.copy()
    channel = output_image[:, :, EMBED_CHANNEL].astype(np.float64)

    full_payload = int_to_fixed_bytes(len(payload), HEADER_SIZE) + payload
    bits = bytes_to_bits(full_payload)

    capacity = max_capacity_bits(image)
    if len(bits) > capacity:
        raise ValueError("Payload too large for DCT image capacity.")

    blocks = list(_iter_blocks(channel))

    for i, bit in enumerate(bits):
        y, x, block = blocks[i]
        centered = block - 128.0
        dct_block = _dct2(centered)

        r, c = COEFF_POS
        coeff = dct_block[r, c]

        # Quantization Index Modulation (QIM):
        # bit 0 is stored near 25% of the quantization interval,
        # bit 1 is stored near 75% of the quantization interval.
        # This is more stable than changing coefficient parity by only 1,
        # because IDCT + uint8 rounding can erase very small coefficient changes.
        base = np.floor(coeff / QUANT_STEP) * QUANT_STEP
        dct_block[r, c] = base + (0.75 * QUANT_STEP if bit == 1 else 0.25 * QUANT_STEP)

        restored = _idct2(dct_block) + 128.0
        channel[y:y + BLOCK_SIZE, x:x + BLOCK_SIZE] = restored

    output_image[:, :, EMBED_CHANNEL] = np.clip(channel, 0, 255).astype(np.uint8)
    return output_image


def extract_dct(image: np.ndarray) -> bytes:
    channel = _get_embedding_channel(image).astype(np.float64)
    bits = []
    target_bits = None

    for _, _, block in _iter_blocks(channel):
        centered = block - 128.0
        dct_block = _dct2(centered)

        r, c = COEFF_POS
        coeff = dct_block[r, c]
        remainder = np.mod(coeff, QUANT_STEP)
        bits.append(1 if remainder >= (QUANT_STEP / 2) else 0)

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
