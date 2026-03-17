import mimetypes

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from backend.app.schemas.decode import DecodeResponse
from backend.app.services.stego_service import extract_secret
from backend.app.utils.s3_storage import (
    S3_DECODED_PREFIX,
    build_object_key,
    try_upload_bytes,
    try_generate_presigned_get_url,
)
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

        decoded_content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        decoded_key = build_object_key(S3_DECODED_PREFIX, file.filename or "decoded_input.png")

        decoded_s3_key = try_upload_bytes(
            data=image_bytes,
            key=decoded_key,
            content_type=decoded_content_type,
        )
        decoded_s3_url = try_generate_presigned_get_url(decoded_s3_key)

        return DecodeResponse(
            plaintext=plaintext,
            # decoded_s3_key=decoded_s3_key,
            decoded_s3_url=decoded_s3_url,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decoding failed: {e}")