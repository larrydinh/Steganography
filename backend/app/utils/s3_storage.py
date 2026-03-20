from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "").strip()
S3_SOURCE_PREFIX = os.getenv("S3_SOURCE_PREFIX", "source/")
S3_ENCODED_PREFIX = os.getenv("S3_ENCODED_PREFIX", "encoded/")
S3_DECODED_PREFIX = os.getenv("S3_DECODED_PREFIX", "decoded/")
S3_RETRIEVAL_PREFIX = os.getenv("S3_RETRIEVAL_PREFIX", "retrieval/")
PRESIGNED_URL_EXPIRES = int(os.getenv("PRESIGNED_URL_EXPIRES", "3600"))
RETRIEVAL_CODE_TTL_HOURS = int(os.getenv("RETRIEVAL_CODE_TTL_HOURS", "24"))

_s3_client = None


def s3_enabled() -> bool:
    return bool(S3_BUCKET_NAME)


from botocore.config import Config


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"},
            ),
        )
    return _s3_client


def _safe_name(filename: str) -> str:
    return os.path.basename(filename or "image.png").replace(" ", "_")


def build_object_key(prefix: str, filename: str) -> str:
    safe_name = _safe_name(filename)
    return f"{prefix}{uuid.uuid4().hex}_{safe_name}"


def build_session_object_key(prefix: str, session_id: str, filename: str) -> str:
    safe_name = _safe_name(filename)
    return f"{prefix}{session_id}/{uuid.uuid4().hex}_{safe_name}"


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


def upload_json(payload: dict[str, Any], key: str) -> str:
    return upload_bytes(
        data=json.dumps(payload).encode("utf-8"),
        key=key,
        content_type="application/json",
    )


def read_json(key: str) -> dict[str, Any]:
    if not s3_enabled():
        raise RuntimeError("S3_BUCKET_NAME is not configured.")

    client = get_s3_client()
    obj = client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
    body = obj["Body"].read().decode("utf-8")
    return json.loads(body)


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


def try_upload_json(payload: dict[str, Any], key: str) -> Optional[str]:
    try:
        return upload_json(payload=payload, key=key)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        logger.exception("S3 JSON upload failed for key %s: %s", key, exc)
        return None


def try_read_json(key: str) -> Optional[dict[str, Any]]:
    try:
        return read_json(key)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        logger.exception("Could not read JSON for key %s: %s", key, exc)
        return None


def try_generate_presigned_get_url(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    try:
        return generate_presigned_get_url(key)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        logger.exception("Could not generate presigned URL for key %s: %s", key, exc)
        return None


def list_objects(prefix: str) -> list[dict[str, Any]]:
    if not s3_enabled():
        return []

    client = get_s3_client()
    paginator = client.get_paginator("list_objects_v2")
    results: list[dict[str, Any]] = []

    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            results.append(
                {
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                }
            )

    return results


def generate_retrieval_code() -> str:
    import random
    import string

    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=4)) + "-" + "".join(random.choices(chars, k=4))


def retrieval_metadata_key(code: str) -> str:
    return f"{S3_RETRIEVAL_PREFIX}{code}.json"


def build_retrieval_metadata(
    *,
    code: str,
    session_id: str,
    file_key: str,
    filename: str,
    kind: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=RETRIEVAL_CODE_TTL_HOURS)
    return {
        "retrieval_code": code,
        "session_id": session_id,
        "file_key": file_key,
        "filename": filename,
        "kind": kind,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }


def is_metadata_expired(metadata: dict[str, Any]) -> bool:
    expires_at = metadata.get("expires_at")
    if not expires_at:
        return True
    return datetime.now(timezone.utc) > datetime.fromisoformat(expires_at)