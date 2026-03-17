import base64
import mimetypes

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from backend.app.schemas.encode import EncodeResponse, EncodeMetrics
from backend.app.services.stego_service import embed_secret
from backend.app.services.metrics_service import build_encode_metrics, timed_embed
from backend.app.services.crypto_service import build_secure_payload
from backend.app.utils.s3_storage import (
    S3_SOURCE_PREFIX,
    S3_ENCODED_PREFIX,
    build_object_key,
    try_upload_bytes,
    try_generate_presigned_get_url,
)
from shared.utils.image_utils import load_image_from_bytes, save_image_to_png_bytes

router = APIRouter()


@router.post("/encode", response_model=EncodeResponse)
async def encode_image(
    file: UploadFile = File(...),
    secret_text: str = Form(...),
    password: str = Form(...),
    method: str = Form(...),
):
    try:
        image_bytes = await file.read()
        image = load_image_from_bytes(image_bytes)

        payload = build_secure_payload(secret_text, password)
        stego_image, embed_time = timed_embed(embed_secret, image, secret_text, password, method)

        metrics = build_encode_metrics(
            original_image=image,
            stego_image=stego_image,
            payload_bytes=len(payload),
            embed_time=embed_time,
        )

        stego_bytes = save_image_to_png_bytes(stego_image)
        stego_filename = f"stego_{method.lower()}.png"
        stego_base64 = base64.b64encode(stego_bytes).decode("utf-8")

        # S3 upload
        source_content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        encoded_content_type = "image/png"

        source_key = build_object_key(S3_SOURCE_PREFIX, file.filename or "source.png")
        encoded_key = build_object_key(S3_ENCODED_PREFIX, stego_filename)

        source_s3_key = try_upload_bytes(
            data=image_bytes,
            key=source_key,
            content_type=source_content_type,
        )
        encoded_s3_key = try_upload_bytes(
            data=stego_bytes,
            key=encoded_key,
            content_type=encoded_content_type,
        )

        # source_s3_url = try_generate_presigned_get_url(source_s3_key)
        encoded_s3_url = try_generate_presigned_get_url(encoded_s3_key)

        return EncodeResponse(
            filename=stego_filename,
            image_base64=stego_base64,
            metrics=EncodeMetrics(**metrics),
            # source_s3_key=source_s3_key,
            # encoded_s3_key=encoded_s3_key,
            # source_s3_url=source_s3_url,
            encoded_s3_url=encoded_s3_url,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))