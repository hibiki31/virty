import base64
import binascii
import json
import os
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENCRYPTION_KEY_ENV = "AGENT_TASK_ENCRYPTION_KEY"
ENCRYPTED_REQUEST_MARKER = "__virty_agent_task_encrypted__"
ENCRYPTED_REQUEST_VERSION = 1
ENCRYPTED_REQUEST_ALGORITHM = "A256GCM"
NONCE_BYTES = 12


class TaskRequestCryptoError(Exception):
    error_code = "TASK_REQUEST_CRYPTO_FAILED"
    retryable = False
    outcome_unknown = False
    safe_message = True


class TaskRequestEncryptionConfigurationError(TaskRequestCryptoError):
    error_code = "TASK_REQUEST_ENCRYPTION_KEY_INVALID"


class TaskRequestDecryptionError(TaskRequestCryptoError):
    error_code = "TASK_REQUEST_DECRYPTION_FAILED"


def _decode_base64url(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    try:
        return base64.b64decode(
            padded.encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise TaskRequestEncryptionConfigurationError(
            "Agent task暗号鍵はbase64url形式で設定してください",
        ) from exc


def _encode_base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _load_key() -> bytes:
    encoded = os.getenv(ENCRYPTION_KEY_ENV)
    if not encoded:
        raise TaskRequestEncryptionConfigurationError(
            "Agent task暗号鍵が設定されていません",
        )
    key = _decode_base64url(encoded)
    if len(key) != 32:
        raise TaskRequestEncryptionConfigurationError(
            "Agent task暗号鍵は32 byteで設定してください",
        )
    return key


def _associated_data(task_uuid: str) -> bytes:
    return (
        f"virty-agent-task-request:v{ENCRYPTED_REQUEST_VERSION}:{task_uuid}"
    ).encode("utf-8")


def encrypt_task_request(plaintext: str, *, task_uuid: str) -> str:
    """Agent task requestをAES-256-GCMで暗号化したJSON wrapperを返す。"""

    nonce = os.urandom(NONCE_BYTES)
    ciphertext = AESGCM(_load_key()).encrypt(
        nonce,
        plaintext.encode("utf-8"),
        _associated_data(task_uuid),
    )
    wrapper = {
        ENCRYPTED_REQUEST_MARKER: True,
        "version": ENCRYPTED_REQUEST_VERSION,
        "algorithm": ENCRYPTED_REQUEST_ALGORITHM,
        "nonce": _encode_base64url(nonce),
        "ciphertext": _encode_base64url(ciphertext),
    }
    return json.dumps(wrapper, ensure_ascii=False, separators=(",", ":"))


def _parse_wrapper(value: Any) -> dict[str, Any] | None:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(value, dict) or value.get(ENCRYPTED_REQUEST_MARKER) is not True:
        return None
    return value


def is_encrypted_task_request(value: Any) -> bool:
    return _parse_wrapper(value) is not None


def decrypt_task_request(value: Any, *, task_uuid: str) -> str:
    """暗号wrapperを検証・復号する。改ざん時は平文を返さない。"""

    wrapper = _parse_wrapper(value)
    if wrapper is None:
        raise TaskRequestDecryptionError("Agent task requestが暗号化されていません")
    if (
        wrapper.get("version") != ENCRYPTED_REQUEST_VERSION
        or wrapper.get("algorithm") != ENCRYPTED_REQUEST_ALGORITHM
        or not isinstance(wrapper.get("nonce"), str)
        or not isinstance(wrapper.get("ciphertext"), str)
    ):
        raise TaskRequestDecryptionError("Agent task requestの暗号形式が不正です")

    try:
        nonce = _decode_base64url(wrapper["nonce"])
        ciphertext = _decode_base64url(wrapper["ciphertext"])
    except TaskRequestEncryptionConfigurationError as exc:
        raise TaskRequestDecryptionError(
            "Agent task requestの暗号encodingが不正です",
        ) from exc

    try:
        if len(nonce) != NONCE_BYTES:
            raise ValueError("invalid nonce length")
        plaintext = AESGCM(_load_key()).decrypt(
            nonce,
            ciphertext,
            _associated_data(task_uuid),
        )
        return plaintext.decode("utf-8")
    except TaskRequestEncryptionConfigurationError:
        raise
    except (InvalidTag, UnicodeDecodeError, ValueError) as exc:
        raise TaskRequestDecryptionError(
            "Agent task requestの復号またはintegrity検査に失敗しました",
        ) from exc


def redact_encrypted_task_request(value: Any) -> Any:
    if is_encrypted_task_request(value):
        return json.dumps({"redacted": True}, separators=(",", ":"))
    return value
