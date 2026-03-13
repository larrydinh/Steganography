from pydantic import BaseModel


class EncodeMetrics(BaseModel):
    psnr: float
    ssim: float
    bpp: float
    embed_time_sec: float


class EncodeResponse(BaseModel):
    filename: str
    image_base64: str
    metrics: EncodeMetrics