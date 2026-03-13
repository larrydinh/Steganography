import base64

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from backend.app.schemas.encode import EncodeResponse, EncodeMetrics
from backend.app.services.stego_service import embed_secret
from backend.app.services.metrics_service import build_encode_metrics, timed_embed
from backend.app.services.crypto_service import build_secure_payload
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
        stego_base64 = base64.b64encode(stego_bytes).decode("utf-8")

        return EncodeResponse(
            filename=f"stego_{method.lower()}.png",
            image_base64=stego_base64,
            metrics=EncodeMetrics(**metrics),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))