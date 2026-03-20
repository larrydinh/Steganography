import mimetypes

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from backend.app.schemas.decode import DecodeResponse, RetrieveRequest, RetrieveResponse
from backend.app.services.stego_service import extract_secret
from backend.app.utils.s3_storage import (
    S3_DECODED_PREFIX,
    RETRIEVAL_CODE_TTL_HOURS,
    build_session_object_key,
    build_retrieval_metadata,
    generate_retrieval_code,
    retrieval_metadata_key,
    try_upload_bytes,
    try_upload_json,
    try_read_json,
    try_generate_presigned_get_url,
    is_metadata_expired,
)

from shared.utils.image_utils import load_image_from_bytes

router = APIRouter()


@router.post("/decode", response_model=DecodeResponse)
async def decode_image(
    file: UploadFile = File(...),
    password: str = Form(...),
    method: str = Form(...),
    session_id: str = Form(...),
):
    try:
        image_bytes = await file.read()
        image = load_image_from_bytes(image_bytes)
        plaintext = extract_secret(image, password, method)

        decoded_content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        decoded_filename = file.filename or "decoded_input.png"
        decoded_key = build_session_object_key(S3_DECODED_PREFIX, session_id, decoded_filename)

        decoded_s3_key = try_upload_bytes(
            data=image_bytes,
            key=decoded_key,
            content_type=decoded_content_type,
        )
        decoded_s3_url = try_generate_presigned_get_url(decoded_s3_key)

        retrieval_code = None
        if decoded_s3_key:
            retrieval_code = generate_retrieval_code()
            metadata = build_retrieval_metadata(
                code=retrieval_code,
                session_id=session_id,
                file_key=decoded_s3_key,
                filename=decoded_filename,
                kind="decoded",
            )
            try_upload_json(metadata, retrieval_metadata_key(retrieval_code))

        return DecodeResponse(
            plaintext=plaintext,
            decoded_s3_url=decoded_s3_url,
            retrieval_code=retrieval_code,
            retrieval_expires_in_hours=RETRIEVAL_CODE_TTL_HOURS if retrieval_code else None,
            session_id=session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decoding failed: {e}")


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_file(request: RetrieveRequest):
    code = request.retrieval_code.strip().upper()
    metadata = try_read_json(retrieval_metadata_key(code))

    if not metadata:
        raise HTTPException(status_code=404, detail="Invalid retrieval code.")

    if is_metadata_expired(metadata):
        raise HTTPException(status_code=410, detail="This retrieval code has expired.")

    file_url = try_generate_presigned_get_url(metadata["file_key"])

    return RetrieveResponse(
        filename=metadata["filename"],
        file_url=file_url,
        kind=metadata["kind"],
        session_id=metadata.get("session_id"),
    )