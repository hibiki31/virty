"""秘密値を保持しないappend-only監査event writer。"""

from datetime import timedelta
import re
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .exceptions import AuditWriteError
from .models import AuditEventModel, new_agent_model, utc_now

AUDIT_RETENTION_DAYS = 365
_SECRET_KEYS = {
    "accesstoken",
    "authorization",
    "clientdatajson",
    "credentialpublickey",
    "currentpassword",
    "dpop",
    "hashedpassword",
    "password",
    "privatekey",
    "rawid",
    "secret",
    "signature",
    "token",
    "vncpassword",
    "webauthnassertion",
}
_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----.*?"
    r"-----END (?:[A-Z0-9 ]+ )?PRIVATE KEY-----",
    re.DOTALL,
)
_JWT_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{10,}\."
    r"[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}(?![A-Za-z0-9_-])",
)
_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(password|passwd|secret|token|authorization|private[_-]?key)"
    r"\s*([:=])\s*(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
)


def _normalized_key(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum())


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            normalized = _normalized_key(key_text)
            if normalized in _SECRET_KEYS or any(
                marker in normalized
                for marker in ("password", "privatekey", "secret", "token")
            ):
                redacted[key_text] = "[REDACTED]"
            else:
                redacted[key_text] = redact_secrets(item)
        return redacted
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    if isinstance(value, tuple):
        return [redact_secrets(item) for item in value]
    if isinstance(value, bytes):
        return "[BINARY]"
    if isinstance(value, str):
        sanitized = _PRIVATE_KEY_PATTERN.sub("[REDACTED PRIVATE KEY]", value)
        sanitized = _JWT_PATTERN.sub("[REDACTED JWT]", sanitized)
        return _ASSIGNMENT_PATTERN.sub(
            lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]",
            sanitized,
        )
    return value


def append_audit_event(
    db: Session,
    *,
    event_type: str,
    actor_id: str,
    policy_decision: str,
    device_id: str | None = None,
    lease_id: str | None = None,
    action_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    project_id: str | None = None,
    node_id: str | None = None,
    request_hash: str | None = None,
    operation_id: str | None = None,
    correlation_id: str | None = None,
    outcome: str | None = None,
    detail: dict[str, Any] | None = None,
) -> AuditEventModel:
    now = utc_now()
    model = new_agent_model(
        AuditEventModel,
        occurred_at=now,
        retention_until=now + timedelta(days=AUDIT_RETENTION_DAYS),
        event_type=event_type,
        actor_id=actor_id,
        device_id=device_id,
        lease_id=lease_id,
        action_id=action_id,
        resource_type=resource_type,
        resource_id=resource_id,
        project_id=project_id,
        node_id=node_id,
        request_hash=request_hash,
        policy_decision=policy_decision,
        operation_id=operation_id,
        correlation_id=correlation_id,
        outcome=outcome,
        detail=redact_secrets(detail or {}),
    )
    try:
        db.add(model)
        db.flush()
    except SQLAlchemyError as exc:
        raise AuditWriteError() from exc
    return model
