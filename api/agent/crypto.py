"""P-256端末鍵、DPoP proof、能力lease JWTの暗号処理。"""

import base64
import binascii
import hashlib
import json
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import SplitResult, urlsplit, urlunsplit

import jwt
from jwt.exceptions import InvalidKeyError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from settings import IS_DEV

from .exceptions import AuthenticationError, ConflictError, ServiceUnavailableError
from .models import AgentDeviceModel, AgentDpopReplayModel, new_agent_model

AGENT_AUDIENCE = "virty-agent-api"
AGENT_ISSUER = "virty"
LEASE_ALGORITHM = "HS256"
DPoP_CLOCK_SKEW_SECONDS = 60
DPoP_REPLAY_TTL_SECONDS = 300
DEV_LEASE_SIGNING_KEY = "virty-agent-development-key-only"


def utc_now() -> datetime:
    return datetime.now(UTC)


def lease_signing_key() -> str:
    value = os.getenv("AGENT_LEASE_SIGNING_KEY")
    if value:
        if len(value) < 32:
            raise ServiceUnavailableError(
                "agent_signing_key_too_short",
                "AGENT_LEASE_SIGNING_KEYは32文字以上にしてください",
            )
        return value
    if IS_DEV:
        return DEV_LEASE_SIGNING_KEY
    raise ServiceUnavailableError(
        "agent_signing_key_missing",
        "AGENT_LEASE_SIGNING_KEYが設定されていません",
    )


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def base64url_decode(value: str) -> bytes:
    if not isinstance(value, str):
        raise AuthenticationError(
            "invalid_device_key",
            "端末公開鍵のbase64url値が不正です",
        )
    padding = "=" * (-len(value) % 4)
    try:
        return base64.b64decode(
            (value + padding).encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
    except (binascii.Error, UnicodeEncodeError, ValueError) as exc:
        raise AuthenticationError(
            "invalid_device_key",
            "端末公開鍵のbase64url値が不正です",
        ) from exc


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: bytes | str) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def request_hash(value: Any) -> str:
    return sha256_hex(canonical_json(value))


def jwk_thumbprint(jwk: dict[str, str]) -> str:
    required = {"crv", "kty", "x", "y"}
    if set(jwk) != required:
        raise AuthenticationError(
            "invalid_device_key",
            "端末公開鍵はP-256公開JWKだけを指定してください",
        )
    if jwk.get("kty") != "EC" or jwk.get("crv") != "P-256":
        raise AuthenticationError(
            "invalid_device_key",
            "端末公開鍵はP-256である必要があります",
        )
    if len(base64url_decode(jwk["x"])) != 32 or len(base64url_decode(jwk["y"])) != 32:
        raise AuthenticationError(
            "invalid_device_key",
            "P-256座標は32 byteである必要があります",
        )
    try:
        jwt.PyJWK.from_dict(jwk)
    except (InvalidKeyError, ValueError) as exc:
        raise AuthenticationError(
            "invalid_device_key",
            "端末公開鍵がP-256曲線上の有効な点ではありません",
        ) from exc
    canonical = {key: jwk[key] for key in sorted(required)}
    return base64url_encode(hashlib.sha256(canonical_json(canonical)).digest())


def pairing_code() -> str:
    return secrets.token_urlsafe(24)


def pairing_code_hash(code: str) -> str:
    return sha256_hex(code)


def normalize_htu(url: str) -> str:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower()
    port = parts.port
    if port is not None and not (
        (scheme == "https" and port == 443) or (scheme == "http" and port == 80)
    ):
        host = f"{hostname}:{port}"
    else:
        host = hostname
    normalized = SplitResult(scheme, host, parts.path or "/", "", "")
    return urlunsplit(normalized)


def expected_htu(path: str) -> str:
    """proxy headerではなく管理者固定の公開base URLからDPoP htuを作る。"""

    public_base = os.getenv("AGENT_PUBLIC_BASE_URL")
    if not public_base:
        raise ServiceUnavailableError(
            "agent_public_base_url_missing",
            "AGENT_PUBLIC_BASE_URLが設定されていません",
        )
    base = normalize_htu(public_base).rstrip("/")
    normalized_path = "/" + path.lstrip("/")
    return f"{base}{normalized_path}"


@dataclass(frozen=True)
class DPoPClaims:
    jti: str
    issued_at: datetime
    thumbprint: str


def verify_dpop_proof(
    db: Session,
    *,
    proof: str,
    device: AgentDeviceModel,
    method: str,
    url: str,
    access_token: str | None = None,
    now: datetime | None = None,
) -> DPoPClaims:
    """DPoP proofを検証し、jtiをbusiness transactionと独立して消費する。"""

    current = now or utc_now()
    try:
        header = jwt.get_unverified_header(proof)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("invalid_dpop", "DPoP headerが不正です") from exc

    if str(header.get("typ", "")).lower() != "dpop+jwt":
        raise AuthenticationError("invalid_dpop", "DPoP typが不正です")
    if header.get("alg") != "ES256":
        raise AuthenticationError("invalid_dpop", "DPoP algはES256に限定されます")
    header_jwk = header.get("jwk")
    if not isinstance(header_jwk, dict):
        raise AuthenticationError("invalid_dpop", "DPoP公開JWKがありません")
    thumbprint = jwk_thumbprint(header_jwk)
    if not secrets.compare_digest(thumbprint, device.public_key_thumbprint):
        raise AuthenticationError(
            "device_key_mismatch",
            "DPoP proofが登録端末鍵に束縛されていません",
        )

    try:
        key = jwt.PyJWK.from_dict(header_jwk).key
        claims = jwt.decode(
            proof,
            key=key,
            algorithms=["ES256"],
            options={
                "verify_aud": False,
                "verify_iat": False,
                "verify_jti": False,
                "require": ["htm", "htu", "iat", "jti"],
            },
        )
    except jwt.PyJWTError as exc:
        raise AuthenticationError("invalid_dpop", "DPoP署名が不正です") from exc

    htm = claims.get("htm")
    htu = claims.get("htu")
    issued = claims.get("iat")
    jti_claim = claims.get("jti")
    if (
        not isinstance(htm, str)
        or not isinstance(htu, str)
        or not isinstance(jti_claim, str)
        or isinstance(issued, bool)
        or not isinstance(issued, int)
    ):
        raise AuthenticationError(
            "invalid_dpop",
            "DPoP claimの型が不正です",
        )
    if htm.upper() != method.upper():
        raise AuthenticationError("dpop_method_mismatch", "DPoP htmが一致しません")
    if normalize_htu(htu) != normalize_htu(url):
        raise AuthenticationError("dpop_uri_mismatch", "DPoP htuが一致しません")
    try:
        issued_at = datetime.fromtimestamp(issued, UTC)
    except (TypeError, ValueError, OSError) as exc:
        raise AuthenticationError("invalid_dpop", "DPoP iatが不正です") from exc
    if abs((current - issued_at).total_seconds()) > DPoP_CLOCK_SKEW_SECONDS:
        raise AuthenticationError("stale_dpop", "DPoP proofの有効時刻外です")
    jti = jti_claim
    if not jti or len(jti) > 128:
        raise AuthenticationError("invalid_dpop", "DPoP jtiが不正です")

    if access_token is not None:
        expected_ath = base64url_encode(
            hashlib.sha256(access_token.encode("ascii")).digest()
        )
        supplied_ath = claims.get("ath")
        if not isinstance(supplied_ath, str) or not secrets.compare_digest(
            expected_ath,
            supplied_ath,
        ):
            raise AuthenticationError(
                "dpop_token_mismatch",
                "DPoP proofが能力lease tokenに束縛されていません",
            )

    _consume_dpop_replay(
        db,
        device_id=device.id,
        jti=jti,
        now=current,
    )
    device.last_seen_at = current
    return DPoPClaims(jti=jti, issued_at=issued_at, thumbprint=thumbprint)


def _consume_dpop_replay(
    db: Session,
    *,
    device_id: str,
    jti: str,
    now: datetime,
) -> None:
    """後段の4xx/rollbackに影響されない独立transactionでproofを消費する。

    呼出し前にdevice行を`FOR UPDATE`してはならない。PostgreSQLの外部key検査と
    競合するため、呼出し側は検証後に必要なrow lockを取得して状態を再検査する。
    """

    bind = db.get_bind()
    # SessionがConnectionへbindされたtestでも、可能なら別connectionを取得する。
    replay_bind = getattr(bind, "engine", bind)
    try:
        with Session(bind=replay_bind) as replay_db:
            replay_db.query(AgentDpopReplayModel).filter(
                AgentDpopReplayModel.expires_at <= now,
            ).delete(synchronize_session=False)
            replay_db.add(new_agent_model(
                AgentDpopReplayModel,
                device_id=device_id,
                jti=jti,
                seen_at=now,
                expires_at=now + timedelta(seconds=DPoP_REPLAY_TTL_SECONDS),
            ))
            replay_db.commit()
    except IntegrityError as exc:
        raise ConflictError("dpop_replay", "DPoP proofは既に使用されています") from exc
    except Exception as exc:
        raise ServiceUnavailableError(
            "dpop_replay_store_unavailable",
            "DPoP replay台帳を確定できないためrequestを拒否しました",
        ) from exc


def create_capability_token(
    *,
    lease_id: str,
    jti: str,
    principal_id: str,
    device_id: str,
    device_thumbprint: str,
    scopes: list[str],
    project_ids: list[str],
    node_ids: list[str],
    max_mutations: int,
    allow_destructive: bool,
    allow_delete_without_recovery: bool,
    allow_network_change_without_oob: bool,
    issued_at: datetime,
    expires_at: datetime,
) -> str:
    claims = {
        "iss": AGENT_ISSUER,
        "aud": AGENT_AUDIENCE,
        "sub": principal_id,
        "iat": int(issued_at.timestamp()),
        "nbf": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": jti,
        "lease_id": lease_id,
        "device_id": device_id,
        "scopes": scopes,
        "projects": project_ids,
        "nodes": node_ids,
        "max_mutations": max_mutations,
        "allow_destructive": allow_destructive,
        "allow_delete_without_recovery": allow_delete_without_recovery,
        "allow_network_change_without_oob": allow_network_change_without_oob,
        "cnf": {"jkt": device_thumbprint},
    }
    return jwt.encode(claims, lease_signing_key(), algorithm=LEASE_ALGORITHM)


def decode_capability_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            lease_signing_key(),
            algorithms=[LEASE_ALGORITHM],
            audience=AGENT_AUDIENCE,
            issuer=AGENT_ISSUER,
            options={
                "require": [
                    "iss",
                    "aud",
                    "sub",
                    "iat",
                    "nbf",
                    "exp",
                    "jti",
                    "lease_id",
                    "device_id",
                    "cnf",
                ]
            },
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("lease_expired", "能力leaseの有効期限が切れています") from exc
    except jwt.PyJWTError as exc:
        raise AuthenticationError("invalid_lease", "能力lease tokenが不正です") from exc


def new_uuid() -> str:
    return str(uuid.uuid4())
