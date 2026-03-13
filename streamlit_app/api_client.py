import os
import requests
from typing import Any

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT_SECONDS = 60


class APIClientError(Exception):
    pass


def _handle_response(response: requests.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError as exc:
        raise APIClientError(
            f"Backend returned non-JSON response (status {response.status_code})."
        ) from exc

    if not response.ok:
        detail = data.get("detail", f"HTTP {response.status_code}")
        raise APIClientError(str(detail))

    return data


def health_check() -> dict[str, Any]:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise APIClientError(f"Could not connect to backend: {exc}") from exc
    return _handle_response(response)


def encode_image(
    file_bytes: bytes,
    filename: str,
    secret_text: str,
    password: str,
    method: str,
) -> dict[str, Any]:
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    data = {
        "secret_text": secret_text,
        "password": password,
        "method": method,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/encode",
            files=files,
            data=data,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise APIClientError(f"Could not connect to backend: {exc}") from exc

    return _handle_response(response)


def decode_image(
    file_bytes: bytes,
    filename: str,
    password: str,
    method: str,
) -> dict[str, Any]:
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    data = {
        "password": password,
        "method": method,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/decode",
            files=files,
            data=data,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise APIClientError(f"Could not connect to backend: {exc}") from exc

    return _handle_response(response)
