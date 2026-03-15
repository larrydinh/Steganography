from __future__ import annotations

import io

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from backend.app.schemas.detect import DetectionResponse
from backend.app.services.detection.detector_router import analyze_image


router = APIRouter(prefix="/detect", tags=["detect"])


@router.post("/analyze", response_model=DetectionResponse)
async def detect_stego(
    file: UploadFile = File(...),
    mode: str = Form("auto"),
    target: str = Form("auto"),
    explain: bool = Form(True),
) -> DetectionResponse:
    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        image.load()  # force full validation/load
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read image: {exc}") from exc

    try:
        result = analyze_image(
            image=image,
            filename=file.filename or "uploaded_image",
            mode=mode,
            target=target,
            explain=explain,
        )
        return DetectionResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Detection failed: {exc}") from exc