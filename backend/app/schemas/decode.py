from pydantic import BaseModel
from typing import Optional


class DecodeResponse(BaseModel):
    plaintext: str
    decoded_s3_key: Optional[str] = None
    decoded_s3_url: Optional[str] = None