"""P-256 device鍵とRFC 9449 DPoP proofの生成。"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def normalize_htu(url: str) -> str:
    """RFC 9449の``htu``向けにqueryとfragmentを除外する。"""

    parsed = urlsplit(url)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    if not scheme or not host:
        raise ValueError("DPoP htuには絶対URLが必要です")
    port = parsed.port
    default_port = (scheme == "https" and port == 443) or (scheme == "http" and port == 80)
    display_host = f"[{host}]" if ":" in host else host
    authority = display_host if port is None or default_port else f"{display_host}:{port}"
    path = parsed.path or "/"
    return urlunsplit((scheme, authority, path, "", ""))


@dataclass(frozen=True)
class DeviceKey:
    """P-256秘密鍵を保持し、公開JWKとDPoP proofを生成する。"""

    private_key: ec.EllipticCurvePrivateKey

    @classmethod
    def generate(cls) -> DeviceKey:
        return cls(ec.generate_private_key(ec.SECP256R1()))

    @classmethod
    def from_pem(cls, pem: str) -> DeviceKey:
        key = serialization.load_pem_private_key(pem.encode("ascii"), password=None)
        if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(
            key.curve, ec.SECP256R1
        ):
            raise ValueError("device鍵はP-256秘密鍵である必要があります")
        return cls(key)

    def to_pem(self) -> str:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("ascii")

    def public_jwk(self) -> dict[str, str]:
        numbers = self.private_key.public_key().public_numbers()
        return {
            "kty": "EC",
            "crv": "P-256",
            "x": _base64url(numbers.x.to_bytes(32, "big")),
            "y": _base64url(numbers.y.to_bytes(32, "big")),
        }

    def dpop_proof(
        self,
        *,
        method: str,
        url: str,
        access_token: str | None = None,
        now: int | None = None,
        jti: str | None = None,
    ) -> str:
        header = {"typ": "dpop+jwt", "alg": "ES256", "jwk": self.public_jwk()}
        payload: dict[str, object] = {
            "htm": method.upper(),
            "htu": normalize_htu(url),
            "iat": int(time.time()) if now is None else now,
            "jti": str(uuid.uuid4()) if jti is None else jti,
        }
        if access_token is not None:
            payload["ath"] = _base64url(hashlib.sha256(access_token.encode("ascii")).digest())

        encoded_header = _base64url(
            json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        encoded_payload = _base64url(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        der_signature = self.private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
        r, s = decode_dss_signature(der_signature)
        signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
        return f"{encoded_header}.{encoded_payload}.{_base64url(signature)}"
