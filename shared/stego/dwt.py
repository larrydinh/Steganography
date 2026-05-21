import numpy as np
import pywt

from shared.utils.bit_utils import (
    bytes_to_bits,
    bits_to_bytes,
    int_to_fixed_bytes,
    fixed_bytes_to_int,
)

HEADER_SIZE = 4
QUANT_STEP = 16.0
EMBED_CHANNEL = 2  # RGB image: 0=Red, 1=Green, 2=Blue


def _validate_rgb_image(image: np.ndarray) -> None:
    if image.dtype != np.uint8:
        raise ValueError("Image must be uint8.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Image must be RGB with 3 channels.")


def _get_embedding_channel(image: np.ndarray) -> np.ndarray:
    """
    DWT should not convert the whole image to grayscale.
    Instead, embed only in one RGB channel and keep the other channels unchanged.
    This preserves the color of the encoded image.
    """
    _validate_rgb_image(image)
    return image[:, :, EMBED_CHANNEL]


def max_capacity_bits(image: np.ndarray) -> int:
    channel = _get_embedding_channel(image)
    coeffs2 = pywt.dwt2(channel.astype(np.float64), "haar")
    _, (lh, _, _) = coeffs2
    return lh.size


def embed_dwt(image: np.ndarray, payload: bytes) -> np.ndarray:
    _validate_rgb_image(image)

    # Keep the original RGB image. Only modify one channel.
    output_image = image.copy()
    channel = output_image[:, :, EMBED_CHANNEL].astype(np.float64)

    full_payload = int_to_fixed_bytes(len(payload), HEADER_SIZE) + payload
    bits = bytes_to_bits(full_payload)

    coeffs2 = pywt.dwt2(channel, "haar")
    ll, (lh, hl, hh) = coeffs2

    flat_lh = lh.flatten().copy()
    if len(bits) > flat_lh.size:
        raise ValueError("Payload too large for DWT image capacity.")

    for i, bit in enumerate(bits):
        coeff = flat_lh[i]

        # Quantization Index Modulation (QIM):
        # bit 0 is stored near 25% of the quantization interval,
        # bit 1 is stored near 75% of the quantization interval.
        # This is more stable than changing coefficient parity by only 1.
        base = np.floor(coeff / QUANT_STEP) * QUANT_STEP
        flat_lh[i] = base + (0.75 * QUANT_STEP if bit == 1 else 0.25 * QUANT_STEP)

    lh_embedded = flat_lh.reshape(lh.shape)
    reconstructed_channel = pywt.idwt2((ll, (lh_embedded, hl, hh)), "haar")
    reconstructed_channel = np.clip(reconstructed_channel, 0, 255).astype(np.uint8)

    # In case wavelet reconstruction returns one extra row/column for odd image sizes.
    h, w = output_image.shape[:2]
    output_image[:, :, EMBED_CHANNEL] = reconstructed_channel[:h, :w]

    return output_image


def extract_dwt(image: np.ndarray) -> bytes:
    channel = _get_embedding_channel(image).astype(np.float64)

    coeffs2 = pywt.dwt2(channel, "haar")
    _, (lh, _, _) = coeffs2

    bits = []
    target_bits = None

    for coeff in lh.flatten():
        remainder = np.mod(coeff, QUANT_STEP)
        bits.append(1 if remainder >= (QUANT_STEP / 2) else 0)

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
