"""WebAuthn libraryを境界化し、challengeを一度だけ消費する。"""

import json
import os
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Protocol

from sqlalchemy.orm import Session

from .crypto import new_uuid
from .crypto import as_utc
from .exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ServiceUnavailableError,
)
from .models import (
    AgentWebAuthnChallengeModel,
    AgentWebAuthnCredentialModel,
    utc_now,
)

WEBAUTHN_CHALLENGE_MINUTES = 5
MAX_ACTIVE_CHALLENGES_PER_USER = 20
MAX_ACTIVE_CHALLENGES_GLOBAL = 500


@dataclass(frozen=True)
class RegistrationVerification:
    credential_id: str
    credential_public_key: bytes
    sign_count: int


@dataclass(frozen=True)
class AuthenticationVerification:
    new_sign_count: int


class WebAuthnBackend(Protocol):
    def registration_options(
        self,
        *,
        challenge: bytes,
        user_id: str,
        user_name: str,
        excluded_credential_ids: list[str],
    ) -> dict[str, Any]: ...

    def verify_registration(
        self,
        *,
        credential: dict[str, Any],
        expected_challenge: bytes,
    ) -> RegistrationVerification: ...

    def authentication_options(
        self,
        *,
        challenge: bytes,
        credential_ids: list[str],
    ) -> dict[str, Any]: ...

    def verify_authentication(
        self,
        *,
        credential: dict[str, Any],
        expected_challenge: bytes,
        credential_public_key: bytes,
        current_sign_count: int,
    ) -> AuthenticationVerification: ...


class PythonWebAuthnBackend:
    """`webauthn` package (py_webauthn)を使用する本番backend。"""

    def __init__(
        self,
        *,
        rp_id: str | None = None,
        origin: str | None = None,
        rp_name: str | None = None,
    ) -> None:
        self.rp_id = rp_id or os.getenv("AGENT_WEBAUTHN_RP_ID", "localhost")
        self.origin = origin or os.getenv(
            "AGENT_WEBAUTHN_ORIGIN",
            "https://localhost",
        )
        self.rp_name = rp_name or os.getenv("AGENT_WEBAUTHN_RP_NAME", "Virty")

    @staticmethod
    def _imports() -> dict[str, Any]:
        try:
            from webauthn import (
                generate_authentication_options,
                generate_registration_options,
                options_to_json,
                verify_authentication_response,
                verify_registration_response,
            )
            from webauthn.helpers import bytes_to_base64url
            from webauthn.helpers import base64url_to_bytes
            from webauthn.helpers.structs import (
                AuthenticatorSelectionCriteria,
                PublicKeyCredentialDescriptor,
                ResidentKeyRequirement,
                UserVerificationRequirement,
            )
        except ImportError as exc:
            raise ServiceUnavailableError(
                "webauthn_dependency_missing",
                "WebAuthn検証libraryがinstallされていません",
            ) from exc
        return {
            "generate_authentication_options": generate_authentication_options,
            "generate_registration_options": generate_registration_options,
            "options_to_json": options_to_json,
            "verify_authentication_response": verify_authentication_response,
            "verify_registration_response": verify_registration_response,
            "bytes_to_base64url": bytes_to_base64url,
            "base64url_to_bytes": base64url_to_bytes,
            "AuthenticatorSelectionCriteria": AuthenticatorSelectionCriteria,
            "PublicKeyCredentialDescriptor": PublicKeyCredentialDescriptor,
            "ResidentKeyRequirement": ResidentKeyRequirement,
            "UserVerificationRequirement": UserVerificationRequirement,
        }

    def registration_options(
        self,
        *,
        challenge: bytes,
        user_id: str,
        user_name: str,
        excluded_credential_ids: list[str],
    ) -> dict[str, Any]:
        modules = self._imports()
        descriptors = [
            modules["PublicKeyCredentialDescriptor"](
                id=modules["base64url_to_bytes"](credential_id)
            )
            for credential_id in excluded_credential_ids
        ]
        options = modules["generate_registration_options"](
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id.encode("utf-8"),
            user_name=user_name,
            user_display_name=user_name,
            challenge=challenge,
            exclude_credentials=descriptors,
            authenticator_selection=modules["AuthenticatorSelectionCriteria"](
                resident_key=modules["ResidentKeyRequirement"].PREFERRED,
                user_verification=modules["UserVerificationRequirement"].REQUIRED,
            ),
        )
        return json.loads(modules["options_to_json"](options))

    def verify_registration(
        self,
        *,
        credential: dict[str, Any],
        expected_challenge: bytes,
    ) -> RegistrationVerification:
        modules = self._imports()
        try:
            result = modules["verify_registration_response"](
                credential=credential,
                expected_challenge=expected_challenge,
                expected_rp_id=self.rp_id,
                expected_origin=self.origin,
                require_user_verification=True,
            )
        except Exception as exc:
            raise AuthenticationError(
                "invalid_webauthn_registration",
                "WebAuthn登録応答を検証できません",
            ) from exc
        return RegistrationVerification(
            credential_id=modules["bytes_to_base64url"](result.credential_id),
            credential_public_key=result.credential_public_key,
            sign_count=result.sign_count,
        )

    def authentication_options(
        self,
        *,
        challenge: bytes,
        credential_ids: list[str],
    ) -> dict[str, Any]:
        modules = self._imports()
        descriptors = [
            modules["PublicKeyCredentialDescriptor"](
                id=modules["base64url_to_bytes"](credential_id)
            )
            for credential_id in credential_ids
        ]
        options = modules["generate_authentication_options"](
            rp_id=self.rp_id,
            challenge=challenge,
            allow_credentials=descriptors,
            user_verification=modules["UserVerificationRequirement"].REQUIRED,
        )
        return json.loads(modules["options_to_json"](options))

    def verify_authentication(
        self,
        *,
        credential: dict[str, Any],
        expected_challenge: bytes,
        credential_public_key: bytes,
        current_sign_count: int,
    ) -> AuthenticationVerification:
        modules = self._imports()
        try:
            result = modules["verify_authentication_response"](
                credential=credential,
                expected_challenge=expected_challenge,
                expected_rp_id=self.rp_id,
                expected_origin=self.origin,
                credential_public_key=credential_public_key,
                credential_current_sign_count=current_sign_count,
                require_user_verification=True,
            )
        except Exception as exc:
            raise AuthenticationError(
                "invalid_webauthn_assertion",
                "WebAuthn認証応答を検証できません",
            ) from exc
        return AuthenticationVerification(new_sign_count=result.new_sign_count)


class WebAuthnService:
    def __init__(self, backend: WebAuthnBackend | None = None) -> None:
        self.backend = backend or PythonWebAuthnBackend()

    def create_registration_options(
        self,
        db: Session,
        *,
        user_id: str,
    ) -> tuple[AgentWebAuthnChallengeModel, dict[str, Any]]:
        credentials = db.query(AgentWebAuthnCredentialModel).filter(
            AgentWebAuthnCredentialModel.user_id == user_id,
            AgentWebAuthnCredentialModel.revoked_at.is_(None),
        ).all()
        challenge = self._create_challenge(
            db,
            user_id=user_id,
            purpose="registration",
            subject_id=user_id,
        )
        options = self.backend.registration_options(
            challenge=challenge.challenge,
            user_id=user_id,
            user_name=user_id,
            excluded_credential_ids=[item.credential_id for item in credentials],
        )
        return challenge, options

    def complete_registration(
        self,
        db: Session,
        *,
        user_id: str,
        challenge_id: str,
        credential_name: str,
        credential: dict[str, Any],
    ) -> AgentWebAuthnCredentialModel:
        challenge = self._load_challenge(
            db,
            challenge_id=challenge_id,
            user_id=user_id,
            purpose="registration",
            subject_id=user_id,
        )
        result = self.backend.verify_registration(
            credential=credential,
            expected_challenge=challenge.challenge,
        )
        if db.get(AgentWebAuthnCredentialModel, result.credential_id):
            raise ConflictError(
                "webauthn_credential_exists",
                "WebAuthn credentialは既に登録されています",
            )
        now = utc_now()
        model = AgentWebAuthnCredentialModel(
            credential_id=result.credential_id,
            user_id=user_id,
            name=credential_name,
            credential_public_key=result.credential_public_key,
            sign_count=result.sign_count,
            transports=self._transports(credential),
            created_at=now,
        )
        challenge.used_at = now
        db.add(model)
        db.flush()
        return model

    def create_authentication_options(
        self,
        db: Session,
        *,
        user_id: str,
        purpose: str,
        subject_id: str,
    ) -> tuple[AgentWebAuthnChallengeModel, dict[str, Any]]:
        credentials = db.query(AgentWebAuthnCredentialModel).filter(
            AgentWebAuthnCredentialModel.user_id == user_id,
            AgentWebAuthnCredentialModel.revoked_at.is_(None),
        ).all()
        if not credentials:
            raise ConflictError(
                "webauthn_enrollment_required",
                "先にWebAuthn credentialを登録してください",
            )
        challenge = self._create_challenge(
            db,
            user_id=user_id,
            purpose=purpose,
            subject_id=subject_id,
        )
        options = self.backend.authentication_options(
            challenge=challenge.challenge,
            credential_ids=[item.credential_id for item in credentials],
        )
        return challenge, options

    def verify_authentication(
        self,
        db: Session,
        *,
        user_id: str,
        purpose: str,
        subject_id: str,
        challenge_id: str,
        credential: dict[str, Any],
    ) -> AgentWebAuthnCredentialModel:
        challenge = self._load_challenge(
            db,
            challenge_id=challenge_id,
            user_id=user_id,
            purpose=purpose,
            subject_id=subject_id,
        )
        credential_id = str(credential.get("id", ""))
        stored = db.query(AgentWebAuthnCredentialModel).filter(
            AgentWebAuthnCredentialModel.credential_id == credential_id,
            AgentWebAuthnCredentialModel.user_id == user_id,
            AgentWebAuthnCredentialModel.revoked_at.is_(None),
        ).with_for_update().one_or_none()
        if stored is None:
            raise AuthenticationError(
                "unknown_webauthn_credential",
                "登録されていないWebAuthn credentialです",
            )
        result = self.backend.verify_authentication(
            credential=credential,
            expected_challenge=challenge.challenge,
            credential_public_key=stored.credential_public_key,
            current_sign_count=stored.sign_count,
        )
        now = utc_now()
        stored.sign_count = result.new_sign_count
        stored.last_used_at = now
        challenge.used_at = now
        db.flush()
        return stored

    @staticmethod
    def _create_challenge(
        db: Session,
        *,
        user_id: str,
        purpose: str,
        subject_id: str,
    ) -> AgentWebAuthnChallengeModel:
        now = utc_now()
        db.query(AgentWebAuthnChallengeModel).filter(
            AgentWebAuthnChallengeModel.expires_at <= now,
        ).delete(synchronize_session=False)
        active = db.query(AgentWebAuthnChallengeModel.id).filter(
            AgentWebAuthnChallengeModel.used_at.is_(None),
            AgentWebAuthnChallengeModel.expires_at > now,
        )
        if active.filter(
            AgentWebAuthnChallengeModel.user_id == user_id,
        ).count() >= MAX_ACTIVE_CHALLENGES_PER_USER:
            raise ConflictError(
                "webauthn_challenge_capacity_exceeded",
                "この利用者のWebAuthn challenge数が上限に達しています",
            )
        if active.count() >= MAX_ACTIVE_CHALLENGES_GLOBAL:
            raise ConflictError(
                "webauthn_challenge_capacity_exceeded",
                "WebAuthn challenge数が上限に達しています",
            )
        model = AgentWebAuthnChallengeModel(
            id=new_uuid(),
            user_id=user_id,
            purpose=purpose,
            subject_id=subject_id,
            challenge=secrets.token_bytes(32),
            created_at=now,
            expires_at=now + timedelta(minutes=WEBAUTHN_CHALLENGE_MINUTES),
        )
        db.add(model)
        db.flush()
        return model

    @staticmethod
    def _load_challenge(
        db: Session,
        *,
        challenge_id: str,
        user_id: str,
        purpose: str,
        subject_id: str,
    ) -> AgentWebAuthnChallengeModel:
        challenge = db.query(AgentWebAuthnChallengeModel).filter(
            AgentWebAuthnChallengeModel.id == challenge_id,
        ).with_for_update().one_or_none()
        if challenge is None:
            raise NotFoundError("challenge_not_found", "WebAuthn challengeがありません")
        if (
            challenge.user_id != user_id
            or challenge.purpose != purpose
            or challenge.subject_id != subject_id
        ):
            raise AuthenticationError(
                "challenge_mismatch",
                "WebAuthn challengeの対象が一致しません",
            )
        if challenge.used_at is not None:
            raise ConflictError(
                "challenge_replay",
                "WebAuthn challengeは既に使用されています",
            )
        if as_utc(challenge.expires_at) <= utc_now():
            raise AuthenticationError(
                "challenge_expired",
                "WebAuthn challengeの有効期限が切れています",
            )
        return challenge

    @staticmethod
    def _transports(credential: dict[str, Any]) -> list[str]:
        response = credential.get("response", {})
        transports = response.get("transports", [])
        if not isinstance(transports, list):
            return []
        return [str(item) for item in transports]
