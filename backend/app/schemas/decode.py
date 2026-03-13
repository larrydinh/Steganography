from pydantic import BaseModel


class DecodeResponse(BaseModel):
    plaintext: str