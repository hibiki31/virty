from __future__ import annotations

import base64
import hashlib
import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from virty_mcp.crypto import DeviceKey, normalize_htu


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def test_p256_key_round_trip_and_public_jwk() -> None:
    original = DeviceKey.generate()
    loaded = DeviceKey.from_pem(original.to_pem())
    jwk = loaded.public_jwk()
    assert jwk["kty"] == "EC"
    assert jwk["crv"] == "P-256"
    assert len(_decode(jwk["x"])) == 32
    assert len(_decode(jwk["y"])) == 32


def test_dpop_proof_has_bound_method_url_token_and_valid_raw_es256_signature() -> None:
    key = DeviceKey.generate()
    token = "lease-token-value"
    proof = key.dpop_proof(
        method="post",
        url="https://VIRTY.EXAMPLE:443/api/agent/v1/actions/vm.create?ignored=yes#fragment",
        access_token=token,
        now=1_777_777_777,
        jti="fixed-jti",
    )
    encoded_header, encoded_payload, encoded_signature = proof.split(".")
    header = json.loads(_decode(encoded_header))
    payload = json.loads(_decode(encoded_payload))
    signature = _decode(encoded_signature)

    assert header == {"alg": "ES256", "jwk": key.public_jwk(), "typ": "dpop+jwt"}
    assert payload == {
        "ath": base64.urlsafe_b64encode(hashlib.sha256(token.encode()).digest())
        .rstrip(b"=")
        .decode(),
        "htm": "POST",
        "htu": "https://virty.example/api/agent/v1/actions/vm.create",
        "iat": 1_777_777_777,
        "jti": "fixed-jti",
    }
    assert len(signature) == 64
    r = int.from_bytes(signature[:32], "big")
    s = int.from_bytes(signature[32:], "big")
    key.private_key.public_key().verify(
        encode_dss_signature(r, s),
        f"{encoded_header}.{encoded_payload}".encode(),
        ec.ECDSA(hashes.SHA256()),
    )


def test_normalize_htu_preserves_non_default_port() -> None:
    assert normalize_htu("https://host.example:8443/a?b=1") == "https://host.example:8443/a"
    assert normalize_htu("http://[::1]:8000/a") == "http://[::1]:8000/a"
