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
    RETRIEVAL_CODE_TTL_HOURS,
    build_session_object_key,
    build_retrieval_metadata,
    generate_retrieval_code,
    retrieval_metadata_key,
    try_upload_bytes,
    try_upload_json,
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
    session_id: str = Form(...),
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

        source_content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        encoded_content_type = "image/png"

        source_key = build_session_object_key(S3_SOURCE_PREFIX, session_id, file.filename or "source.png")
        encoded_key = build_session_object_key(S3_ENCODED_PREFIX, session_id, stego_filename)

        try_upload_bytes(
            data=image_bytes,
            key=source_key,
            content_type=source_content_type,
        )
        encoded_s3_key = try_upload_bytes(
            data=stego_bytes,
            key=encoded_key,
            content_type=encoded_content_type,
        )

        encoded_s3_url = try_generate_presigned_get_url(encoded_s3_key)

        retrieval_code = None
        if encoded_s3_key:
            retrieval_code = generate_retrieval_code()
            metadata = build_retrieval_metadata(
                code=retrieval_code,
                session_id=session_id,
                file_key=encoded_s3_key,
                filename=stego_filename,
                kind="encoded",
            )
            try_upload_json(metadata, retrieval_metadata_key(retrieval_code))

        return EncodeResponse(
            filename=stego_filename,
            image_base64=stego_base64,
            metrics=EncodeMetrics(**metrics),
            encoded_s3_url=encoded_s3_url,
            retrieval_code=retrieval_code,
            retrieval_expires_in_hours=RETRIEVAL_CODE_TTL_HOURS if retrieval_code else None,
            session_id=session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))