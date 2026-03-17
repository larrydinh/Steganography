from __future__ import annotations

import logging
import os
import uuid
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "").strip()
S3_SOURCE_PREFIX = os.getenv("S3_SOURCE_PREFIX", "source/")
S3_ENCODED_PREFIX = os.getenv("S3_ENCODED_PREFIX", "encoded/")
S3_DECODED_PREFIX = os.getenv("S3_DECODED_PREFIX", "decoded/")
PRESIGNED_URL_EXPIRES = int(os.getenv("PRESIGNED_URL_EXPIRES", "3600"))

_s3_client = None


def s3_enabled() -> bool:
    return bool(S3_BUCKET_NAME)


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3", region_name=AWS_REGION)
    return _s3_client


def build_object_key(prefix: str, filename: str) -> str:
    safe_name = os.path.basename(filename or "image.png").replace(" ", "_")
    return f"{prefix}{uuid.uuid4().hex}_{safe_name}"


def upload_bytes(data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
    if not s3_enabled():
        raise RuntimeError("S3_BUCKET_NAME is not configured.")

    client = get_s3_client()
    client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key


def generate_presigned_get_url(key: str) -> str:
    if not s3_enabled():
        raise RuntimeError("S3_BUCKET_NAME is not configured.")

    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRES,
    )


def try_upload_bytes(data: bytes, key: str, content_type: str = "application/octet-stream") -> Optional[str]:
    try:
        logger.warning("Attempting S3 upload: bucket=%s key=%s region=%s", S3_BUCKET_NAME, key, AWS_REGION)
        return upload_bytes(data=data, key=key, content_type=content_type)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        logger.exception("S3 upload failed for key %s: %s", key, exc)
        return None


def try_generate_presigned_get_url(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    try:
        return generate_presigned_get_url(key)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        logger.exception("Could not generate presigned URL for key %s: %s", key, exc)
        return None
