from fastapi import FastAPI

from backend.app.api.routes_encode import router as encode_router
from backend.app.api.routes_decode import router as decode_router
from backend.app.api.routes_detect import router as detect_router
app = FastAPI(title="Steganography API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(encode_router)
app.include_router(decode_router)
app.include_router(detect_router)