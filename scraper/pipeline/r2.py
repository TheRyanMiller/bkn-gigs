from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover - dependency is optional when R2 is disabled.
    boto3 = None
    BotoCoreError = ClientError = Exception

from scraper import config

log = logging.getLogger(__name__)

_BKN_APP_PREFIX = "apps/bkn-gigs/"
_SHARED_ARTIST_CACHE_KEYS = {
    "shared/artist-cache.json",
    "shared/artist-spotify-cache.json",
}


def _join(prefix: str, name: str) -> str:
    key = f"{prefix.strip('/')}/{name.strip('/')}"
    if "/" not in key:
        raise ValueError(f"R2 key is not namespaced: {key}")
    return key


def _ensure_allowed_key(key: str) -> str:
    normalized = key.strip("/")
    if normalized.startswith(_BKN_APP_PREFIX) or normalized in _SHARED_ARTIST_CACHE_KEYS:
        return normalized
    raise ValueError(f"R2 key is outside the BKN Gigs namespace: {normalized}")


def public_key(name: str) -> str:
    return _ensure_allowed_key(_join(config.R2_PUBLIC_PREFIX, name))


def state_key(name: str) -> str:
    return _ensure_allowed_key(_join(config.R2_STATE_PREFIX, name))


def shared_key(name: str) -> str:
    return _ensure_allowed_key(_join(config.R2_SHARED_PREFIX, name))


def r2_enabled() -> bool:
    return bool(
        boto3
        and
        config.R2_BUCKET_NAME
        and config.R2_ENDPOINT_URL
        and config.R2_ACCESS_KEY_ID
        and config.R2_SECRET_ACCESS_KEY
    )


def client():
    if not r2_enabled():
        return None
    return boto3.client(
        "s3",
        endpoint_url=config.R2_ENDPOINT_URL,
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def download_json(key: str, default: Any) -> Any:
    key = _ensure_allowed_key(key)
    r2 = client()
    if not r2:
        return default
    try:
        response = r2.get_object(Bucket=config.R2_BUCKET_NAME, Key=key)
        return json.loads(response["Body"].read().decode("utf-8"))
    except (ClientError, BotoCoreError, json.JSONDecodeError) as exc:
        log.info("Could not load R2 object %s: %s", key, exc)
        return default


def upload_json(key: str, data: Any) -> None:
    key = _ensure_allowed_key(key)
    r2 = client()
    if not r2:
        return
    body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    r2.put_object(
        Bucket=config.R2_BUCKET_NAME,
        Key=key,
        Body=body,
        ContentType="application/json",
    )


def upload_file(key: str, path: Path, content_type: str = "text/plain") -> None:
    key = _ensure_allowed_key(key)
    r2 = client()
    if not r2 or not path.exists():
        return
    r2.upload_file(
        str(path),
        config.R2_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type},
    )
