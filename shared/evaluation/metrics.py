import time
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def compute_psnr(original: np.ndarray, modified: np.ndarray) -> float:
    return float(peak_signal_noise_ratio(original, modified, data_range=255))


def compute_ssim(original: np.ndarray, modified: np.ndarray) -> float:
    return float(structural_similarity(original, modified, channel_axis=2, data_range=255))


def compute_bpp(payload_bytes: int, image_shape: tuple[int, ...]) -> float:
    h, w = image_shape[:2]
    return (payload_bytes * 8) / (h * w)


def timed_call(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed