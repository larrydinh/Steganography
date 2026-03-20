from pydantic import BaseModel
from typing import Optional

class EncodeMetrics(BaseModel):
    psnr: float
    ssim: float
    bpp: float
    embed_time_sec: float


class EncodeResponse(BaseModel):
    filename: str
    image_base64: str
    metrics: EncodeMetrics
    # source_s3_key: Optional[str] = None
    # encoded_s3_key: Optional[str] = None
    # source_s3_url: Optional[str] = None
    encoded_s3_url: Optional[str] = None
    retrieval_code: Optional[str] = None
    retrieval_expires_in_hours: Optional[int] = None
    session_id: Optional[str] = None