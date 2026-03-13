from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from backend.app.schemas.decode import DecodeResponse
from backend.app.services.stego_service import extract_secret
from shared.utils.image_utils import load_image_from_bytes

router = APIRouter()


@router.post("/decode", response_model=DecodeResponse)
async def decode_image(
    file: UploadFile = File(...),
    password: str = Form(...),
    method: str = Form(...),
):
    try:
        image_bytes = await file.read()
        image = load_image_from_bytes(image_bytes)
        plaintext = extract_secret(image, password, method)
        return DecodeResponse(plaintext=plaintext)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decoding failed: {e}")