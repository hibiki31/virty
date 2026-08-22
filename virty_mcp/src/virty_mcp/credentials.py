"""OS credential storeとVirty device profileの抽象。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol


class CredentialStoreError(RuntimeError):
    """安全なcredential storeを利用できない場合の例外。"""


class CredentialStore(Protocol):
    """秘密値を保存する最小interface。"""

    def get_secret(self, name: str) -> str | None:
        """保存済みの秘密値を返す。"""

    def set_secret(self, name: str, value: str) -> None:
        """秘密値を保存または更新する。"""

    def delete_secret(self, name: str) -> None:
        """秘密値を削除する。"""


def _is_os_credential_backend(backend: Any) -> bool:
    """keyring標準のOS backendだけを許可し、file/custom fallbackを拒否する。"""

    backend_name = f"{type(backend).__module__}.{type(backend).__name__}".lower()
    rejected = ("fail", "null", "plaintext", "keyrings.alt", "chainer")
    try:
        priority = float(getattr(backend, "priority", 0))
    except (TypeError, ValueError):
        return False
    return (
        priority > 0
        and backend_name.startswith("keyring.backends.")
        and not any(marker in backend_name for marker in rejected)
    )


class KeyringCredentialStore:
    """keyring経由でOSのcredential storeだけを使用する実装。"""

    _SERVICE_PREFIX = "jp.virty.mcp"

    def __init__(self, profile: str = "default") -> None:
        try:
            import keyring
        except ImportError as exc:  # pragma: no cover - packaging failure
            raise CredentialStoreError("keyring packageが必要です") from exc

        backend = keyring.get_keyring()
        if not _is_os_credential_backend(backend):
            raise CredentialStoreError(
                "安全なOS credential backendが見つかりません。"
                "Secret Service、Keychain、Credential Lockerのいずれかを構成してください"
            )

        self._keyring = keyring
        self._service = f"{self._SERVICE_PREFIX}.{profile}"

    def get_secret(self, name: str) -> str | None:
        return self._keyring.get_password(self._service, name)

    def set_secret(self, name: str, value: str) -> None:
        try:
            self._keyring.set_password(self._service, name, value)
        except Exception as exc:  # keyringはbackend固有例外を公開する
            raise CredentialStoreError(f"credentialを保存できません: {name}") from exc

    def delete_secret(self, name: str) -> None:
        try:
            self._keyring.delete_password(self._service, name)
        except self._keyring.errors.PasswordDeleteError:
            return
        except Exception as exc:
            raise CredentialStoreError(f"credentialを削除できません: {name}") from exc


class MemoryCredentialStore:
    """副作用のないtest向けcredential store。"""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def get_secret(self, name: str) -> str | None:
        return self.values.get(name)

    def set_secret(self, name: str, value: str) -> None:
        self.values[name] = value

    def delete_secret(self, name: str) -> None:
        self.values.pop(name, None)


@dataclass(frozen=True)
class LeaseCredential:
    """OS credential storeに保存する短命lease。"""

    access_token: str
    lease_id: str
    expires_at: str
    max_mutations: int
    origin: str
    device_id: str


class ProfileRepository:
    """device、pairing、leaseの永続状態を名前付き秘密値へ格納する。"""

    _PRIVATE_KEY = "device-private-key-pem"
    _DEVICE = "device-registration"
    _PAIRING = "pending-pairing"
    _LEASE_REQUEST = "pending-lease-request"
    _LEASE = "active-lease"

    def __init__(self, store: CredentialStore) -> None:
        self._store = store

    @property
    def store(self) -> CredentialStore:
        return self._store

    def get_private_key_pem(self) -> str | None:
        return self._store.get_secret(self._PRIVATE_KEY)

    def set_private_key_pem(self, value: str) -> None:
        self._store.set_secret(self._PRIVATE_KEY, value)

    def get_device(self) -> dict[str, Any] | None:
        return self._get_json(self._DEVICE)

    def set_device(self, value: dict[str, Any]) -> None:
        self._set_json(self._DEVICE, value)

    def clear_device(self) -> None:
        self._store.delete_secret(self._DEVICE)

    def get_pairing(self) -> dict[str, Any] | None:
        return self._get_json(self._PAIRING)

    def set_pairing(self, value: dict[str, Any]) -> None:
        self._set_json(self._PAIRING, value)

    def clear_pairing(self) -> None:
        self._store.delete_secret(self._PAIRING)

    def get_lease_request(self) -> dict[str, Any] | None:
        return self._get_json(self._LEASE_REQUEST)

    def set_lease_request(self, value: dict[str, Any]) -> None:
        self._set_json(self._LEASE_REQUEST, value)

    def clear_lease_request(self) -> None:
        self._store.delete_secret(self._LEASE_REQUEST)

    def get_lease(self) -> LeaseCredential | None:
        value = self._get_json(self._LEASE)
        if value is None:
            return None
        try:
            return LeaseCredential(
                access_token=str(value["accessToken"]),
                lease_id=str(value["leaseId"]),
                expires_at=str(value["expiresAt"]),
                max_mutations=int(value["maxMutations"]),
                origin=str(value["origin"]),
                device_id=str(value["deviceId"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise CredentialStoreError("保存済みlease credentialが壊れています") from exc

    def set_lease(self, value: LeaseCredential) -> None:
        self._set_json(
            self._LEASE,
            {
                "accessToken": value.access_token,
                "leaseId": value.lease_id,
                "expiresAt": value.expires_at,
                "maxMutations": value.max_mutations,
                "origin": value.origin,
                "deviceId": value.device_id,
            },
        )

    def clear_lease(self) -> None:
        self._store.delete_secret(self._LEASE)

    def _get_json(self, name: str) -> dict[str, Any] | None:
        raw = self._store.get_secret(name)
        if raw is None:
            return None
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CredentialStoreError(f"保存済みcredentialが壊れています: {name}") from exc
        if not isinstance(value, dict):
            raise CredentialStoreError(f"保存済みcredentialの形式が不正です: {name}")
        return value

    def _set_json(self, name: str, value: dict[str, Any]) -> None:
        self._store.set_secret(
            name,
            json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        )
