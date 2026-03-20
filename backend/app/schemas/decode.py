from pydantic import BaseModel
from typing import Optional


class DecodeResponse(BaseModel):
    plaintext: str
    decoded_s3_url: Optional[str] = None
    retrieval_code: Optional[str] = None
    retrieval_expires_in_hours: Optional[int] = None
    session_id: Optional[str] = None


class RetrieveRequest(BaseModel):
    retrieval_code: str


class RetrieveResponse(BaseModel):
    filename: str
    file_url: Optional[str] = None
    kind: str
    session_id: Optional[str] = None