from shared.evaluation.metrics import compute_psnr, compute_ssim, compute_bpp, timed_call


def build_encode_metrics(original_image, stego_image, payload_bytes: int, embed_time: float) -> dict:
    return {
        "psnr": compute_psnr(original_image, stego_image),
        "ssim": compute_ssim(original_image, stego_image),
        "bpp": compute_bpp(payload_bytes, original_image.shape),
        "embed_time_sec": embed_time,
    }


def timed_embed(func, *args, **kwargs):
    return timed_call(func, *args, **kwargs)