"""Virty Agent APIのHTTPS client。"""

from __future__ import annotations

import json
import os
import re
import ssl
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

from .credentials import LeaseCredential, ProfileRepository
from .crypto import DeviceKey, normalize_htu

MAX_HTTP_RESPONSE_BYTES = 16 * 1024 * 1024
_PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
_QUOTED_PASSWORD_ASSIGNMENT = re.compile(
    r"\b(passwd|password)\s*=\s*(['\"])(.*?)\2",
    re.IGNORECASE | re.DOTALL,
)
_UNQUOTED_PASSWORD_ASSIGNMENT = re.compile(
    r"\b(passwd|password)\s*[:=]\s*([^\s,<>'\"]+)",
    re.IGNORECASE,
)
_JWT_VALUE = re.compile(
    r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"
)


def _replace_known_secrets(value: str, secrets: tuple[str, ...]) -> str:
    """置換markerを後続の短いsecretで再置換せず、既知値をすべて隠す。"""

    segments: list[tuple[str, bool]] = [(value, False)]
    for secret in secrets:
        replaced: list[tuple[str, bool]] = []
        for segment, is_redacted in segments:
            if is_redacted or secret not in segment:
                replaced.append((segment, is_redacted))
                continue
            pieces = segment.split(secret)
            for index, piece in enumerate(pieces):
                if piece:
                    replaced.append((piece, False))
                if index < len(pieces) - 1:
                    replaced.append(("", True))
        segments = replaced
    return "".join("[REDACTED]" if is_redacted else segment for segment, is_redacted in segments)


class _NoRedirectHandler(HTTPRedirectHandler):
    """DPoP/Authorization headerを別originへ転送しないためredirectを拒否する。"""

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Mapping[str, str],
        newurl: str,
    ) -> None:
        return None


class AgentApiError(RuntimeError):
    """Agent APIへの安全な再試行判断に必要なerror。"""

    def __init__(self, message: str, *, status: int | None = None, code: str | None = None):
        super().__init__(message)
        self.status = status
        self.code = code


def redact_secrets(value: Any, *, secret_values: Iterable[str] = ()) -> Any:
    """Agent応答に秘密値が混入してもMCPへ渡さない。

    field名による防御に加えて、write-only入力やlocal credentialの既知値が
    task log等の自由記述fieldへ埋め込まれた場合も値を置換する。
    """

    sensitive = {
        "accesstoken",
        "password",
        "passwordhash",
        "hashedpassword",
        "privatekey",
        "sshprivatekey",
        "vncpassword",
        "webauthnassertion",
        "clientsecret",
        "refreshtoken",
    }
    known_secrets = tuple(
        sorted({secret for secret in secret_values if secret}, key=len, reverse=True)
    )
    if isinstance(value, dict):
        return {
            str(key): (
                "[REDACTED]"
                if re.sub(r"[^a-z0-9]", "", str(key).lower()) in sensitive
                else redact_secrets(child, secret_values=known_secrets)
            )
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(child, secret_values=known_secrets) for child in value]
    if isinstance(value, str):
        redacted = _replace_known_secrets(value, known_secrets)
        redacted = _PRIVATE_KEY_BLOCK.sub("[REDACTED]", redacted)
        redacted = _QUOTED_PASSWORD_ASSIGNMENT.sub(
            lambda match: (
                f"{match.group(1)}={match.group(2)}[REDACTED]{match.group(2)}"
            ),
            redacted,
        )
        redacted = _UNQUOTED_PASSWORD_ASSIGNMENT.sub(
            lambda match: f"{match.group(1)}: [REDACTED]",
            redacted,
        )
        redacted = _JWT_VALUE.sub("[REDACTED]", redacted)
        return redacted
    return value


class HttpTransport(Protocol):
    """testで差し替え可能なHTTP transport。"""

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout: float,
        ssl_context: ssl.SSLContext,
    ) -> tuple[int, Mapping[str, str], bytes]:
        """HTTP requestを実行する。"""


class UrllibTransport:
    """標準libraryだけで通信する同期HTTP transport。"""

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout: float,
        ssl_context: ssl.SSLContext,
    ) -> tuple[int, Mapping[str, str], bytes]:
        request = Request(url=url, data=body, headers=dict(headers), method=method)
        opener = build_opener(
            ProxyHandler({}),
            _NoRedirectHandler(),
            HTTPSHandler(context=ssl_context),
        )
        try:
            with opener.open(request, timeout=timeout) as response:
                raw = response.read(MAX_HTTP_RESPONSE_BYTES + 1)
                if len(raw) > MAX_HTTP_RESPONSE_BYTES:
                    raise AgentApiError("Agent API応答がsize上限を超えています")
                return response.status, dict(response.headers.items()), raw
        except HTTPError as exc:
            raw = exc.read(MAX_HTTP_RESPONSE_BYTES + 1)
            if len(raw) > MAX_HTTP_RESPONSE_BYTES:
                raise AgentApiError(
                    "Agent API error応答がsize上限を超えています", status=exc.code
                ) from exc
            return exc.code, dict(exc.headers.items()), raw
        except (URLError, TimeoutError, OSError) as exc:
            raise AgentApiError("Virty Agent APIへ接続できません") from exc


@dataclass(frozen=True)
class AgentApiConfig:
    """environmentから与えるAgent API接続設定。"""

    base_url: str
    ca_file: str | None = None
    timeout_seconds: float = 30.0
    profile: str = "default"
    allow_insecure_loopback: bool = False

    def __post_init__(self) -> None:
        try:
            parsed = urlsplit(self.base_url)
            parsed_port = parsed.port
        except ValueError as exc:
            raise ValueError("VIRTY_AGENT_BASE_URLの形式またはportが不正です") from exc
        if (
            parsed.scheme == "https" and parsed.hostname is not None
        ) or (
            parsed.scheme == "http"
            and parsed.hostname in {"127.0.0.1", "::1", "localhost"}
            and self.allow_insecure_loopback
        ):
            pass
        else:
            raise ValueError(
                "VIRTY_AGENT_BASE_URLはHTTPSで指定してください。"
                "平文HTTPは明示的に許可したloopback testだけで使用できます"
            )
        explicit_empty_port = (
            parsed_port is None and ":" in parsed.netloc.rsplit("]", 1)[-1]
        )
        if (
            parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
            or parsed.username is not None
            or parsed.password is not None
            or not parsed.hostname
            or explicit_empty_port
        ):
            raise ValueError(
                "VIRTY_AGENT_BASE_URLはcredential、path、query、fragmentを含まないoriginで"
                "指定してください"
            )
        if not 1 <= self.timeout_seconds <= 300:
            raise ValueError("HTTP timeoutは1〜300秒で指定してください")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", self.profile):
            raise ValueError("VIRTY_MCP_PROFILEの形式が不正です")

    @classmethod
    def from_environment(cls) -> AgentApiConfig:
        base_url = os.environ.get("VIRTY_AGENT_BASE_URL")
        if not base_url:
            raise ValueError("VIRTY_AGENT_BASE_URLを設定してください")
        return cls(
            base_url=base_url,
            ca_file=os.environ.get("VIRTY_TLS_CA_FILE") or None,
            timeout_seconds=float(os.environ.get("VIRTY_AGENT_TIMEOUT_SECONDS", "30")),
            profile=os.environ.get("VIRTY_MCP_PROFILE", "default"),
            allow_insecure_loopback=(
                os.environ.get("VIRTY_ALLOW_INSECURE_LOOPBACK", "").lower() == "true"
            ),
        )


class AgentApiClient:
    """端末鍵に束縛されたpairing、lease、action、operation client。"""

    _API_PREFIX = "/api/agent/v1"

    def __init__(
        self,
        *,
        config: AgentApiConfig,
        repository: ProfileRepository,
        transport: HttpTransport | None = None,
    ) -> None:
        self.config = config
        self.repository = repository
        self.transport = transport or UrllibTransport()
        self._ssl_context = ssl.create_default_context(cafile=config.ca_file)
        self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        self._origin = normalize_htu(config.base_url)

    def create_pairing(
        self,
        *,
        device_name: str,
        requested_scopes: list[str],
        replace_key: bool = False,
    ) -> dict[str, Any]:
        existing = self.repository.get_private_key_pem()
        key = (
            DeviceKey.generate()
            if existing is None or replace_key
            else self._device_key()
        )

        response = self._request_json(
            "POST",
            f"{self._API_PREFIX}/pairings",
            body={
                "deviceName": device_name,
                "publicKeyJwk": key.public_jwk(),
                "requestedScopes": requested_scopes,
            },
        )
        self._require_fields(response, "pairingId", "pairingCode", "status", "expiresAt")
        if response["status"] != "pending":
            raise AgentApiError("pending pairing以外の応答を受信しました")
        if existing is None or replace_key:
            # API requestが失敗した場合は旧鍵を保持し、server上deviceへのaccessを失わない。
            self.repository.set_private_key_pem(key.to_pem())
        if replace_key:
            self.repository.clear_lease()
            self.repository.clear_lease_request()
            self.repository.clear_device()
        self.repository.set_pairing({**response, "origin": self._origin})
        return self._without_secrets(response)

    def get_pairing(self) -> dict[str, Any]:
        pairing = self.repository.get_pairing()
        if pairing is None:
            raise AgentApiError("保留中のpairingがありません")
        self._require_origin(pairing)
        response = self._request_json(
            "GET",
            f"{self._API_PREFIX}/pairings/{self._path_segment(pairing['pairingId'])}",
            headers={"X-Pairing-Code": str(pairing["pairingCode"])},
            secret_values=(str(pairing["pairingCode"]),),
        )
        self._require_fields(response, "pairingId", "status", "expiresAt")
        if str(response["pairingId"]) != str(pairing["pairingId"]):
            raise AgentApiError("pairing応答のIDが一致しません")
        status = response["status"]
        if status not in {"pending", "active", "expired", "rejected"}:
            raise AgentApiError("未対応のpairing状態を受信しました")
        if status == "active":
            self._require_fields(response, "deviceId")
            # 新しいdeviceに旧deviceのleaseを結び直さない。
            self.repository.clear_lease()
            self.repository.clear_lease_request()
            self.repository.set_device(
                {
                    "deviceId": response["deviceId"],
                    "pairingId": response["pairingId"],
                    "activatedAt": response.get("activatedAt"),
                    "origin": self._origin,
                }
            )
            self.repository.clear_pairing()
        elif status in {"expired", "rejected"}:
            self.repository.clear_pairing()
        return self._without_secrets(response)

    def begin_lease(
        self,
        *,
        principal_id: str,
        requested_scopes: list[str],
        project_ids: list[str],
        node_ids: list[str],
        max_mutations: int,
        allow_destructive: bool,
        allow_delete_without_recovery: bool,
        allow_network_change_without_oob: bool,
    ) -> dict[str, Any]:
        device = self._device()
        body: dict[str, Any] = {
            "deviceId": device["deviceId"],
            "principalId": principal_id,
            "requestedScopes": requested_scopes,
            "projectIds": project_ids,
            "nodeIds": node_ids,
            "maxMutations": max_mutations,
            "allowDestructive": allow_destructive,
            "allowDeleteWithoutRecovery": allow_delete_without_recovery,
            "allowNetworkChangeWithoutOob": allow_network_change_without_oob,
        }
        response = self._request_with_dpop("POST", f"{self._API_PREFIX}/leases", body=body)
        self._require_fields(response, "kind", "requestId", "status", "expiresAt")
        if response["kind"] != "pending" or response["status"] != "pending":
            raise AgentApiError("pending lease request以外の応答を受信しました")
        self.repository.set_lease_request(
            {"request": body, "pending": response, "origin": self._origin}
        )
        return self._without_secrets(response)

    def get_lease_status(self) -> dict[str, Any]:
        """Virty Web UIでの承認状態をpollし、承認済みならtokenへ交換する。"""

        pending = self.repository.get_lease_request()
        if pending is None:
            raise AgentApiError("保留中のlease requestがありません")
        self._require_origin(pending)
        device = self._device()
        request_device_id = str((pending.get("request") or {}).get("deviceId", ""))
        if request_device_id != str(device["deviceId"]):
            raise AgentApiError("保存済みlease requestが現在のdeviceに属しません")
        request_id = str((pending.get("pending") or {}).get("requestId", ""))
        if not request_id:
            raise AgentApiError("保存済みlease requestが壊れています")
        status_response = self._request_with_dpop(
            "GET", f"{self._API_PREFIX}/leases/{self._path_segment(request_id)}"
        )
        self._require_fields(status_response, "requestId", "deviceId", "status", "expiresAt")
        if str(status_response["requestId"]) != request_id:
            raise AgentApiError("lease request応答のrequest IDが一致しません")
        if str(status_response["deviceId"]) != str(device["deviceId"]):
            raise AgentApiError("lease request応答のdevice IDが一致しません")
        status = status_response["status"]
        if status == "pending":
            return self._without_secrets(status_response)
        if status in {"expired", "rejected"}:
            self.repository.clear_lease_request()
            return self._without_secrets(status_response)
        if status != "approved":
            raise AgentApiError("未対応のlease request状態を受信しました")

        response = self._request_with_dpop(
            "POST",
            f"{self._API_PREFIX}/leases/{self._path_segment(request_id)}/exchange",
            body={},
        )
        self._require_fields(
            response,
            "kind",
            "accessToken",
            "tokenType",
            "expiresAt",
            "leaseId",
            "maxMutations",
        )
        if response["kind"] != "lease" or response["tokenType"] != "DPoP":
            raise AgentApiError("DPoP lease以外の応答を受信しました")
        self.repository.set_lease(
            LeaseCredential(
                access_token=str(response["accessToken"]),
                lease_id=str(response["leaseId"]),
                expires_at=str(response["expiresAt"]),
                max_mutations=int(response["maxMutations"]),
                origin=self._origin,
                device_id=str(device["deviceId"]),
            )
        )
        self.repository.clear_lease_request()
        return {
            "requestId": request_id,
            "status": "active",
            "lease": self._without_secrets(response),
        }

    def call_action(
        self,
        *,
        action: str,
        action_input: dict[str, Any],
        target: dict[str, Any],
        idempotency_key: str | None = None,
        expected_generation: str | None = None,
        secret_values: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"input": action_input, "target": target}
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        if expected_generation is not None:
            body["expectedGeneration"] = expected_generation
        return self._request_with_dpop(
            "POST",
            f"{self._API_PREFIX}/actions/{action}",
            body=body,
            use_lease=True,
            secret_values=secret_values,
        )

    def get_operation(self, operation_id: str) -> dict[str, Any]:
        return self._request_with_dpop(
            "GET",
            f"{self._API_PREFIX}/operations/{self._path_segment(operation_id)}",
            use_lease=True,
        )

    def cancel_operation(self, operation_id: str) -> dict[str, Any]:
        return self._request_with_dpop(
            "POST",
            f"{self._API_PREFIX}/operations/{self._path_segment(operation_id)}",
            body={},
            use_lease=True,
        )

    def session_status(self) -> dict[str, Any]:
        device = self.repository.get_device()
        lease = self.repository.get_lease()
        pending_pairing = self.repository.get_pairing()
        pending_lease = self.repository.get_lease_request()
        device_matches = device is not None and device.get("origin") == self._origin
        pairing_matches = (
            pending_pairing is not None and pending_pairing.get("origin") == self._origin
        )
        pending_lease_matches = (
            pending_lease is not None and pending_lease.get("origin") == self._origin
        )
        lease_matches = (
            lease is not None
            and lease.origin == self._origin
            and device_matches
            and lease.device_id == str(device.get("deviceId"))
        )
        return {
            "paired": device_matches,
            "deviceId": device.get("deviceId") if device_matches else None,
            "pairingPending": pairing_matches,
            "leasePending": pending_lease_matches,
            "originMismatch": any(
                (
                    device is not None and not device_matches,
                    pending_pairing is not None and not pairing_matches,
                    pending_lease is not None and not pending_lease_matches,
                    lease is not None and not lease_matches,
                )
            ),
            "lease": None
            if not lease_matches
            else {
                "leaseId": lease.lease_id,
                "expiresAt": lease.expires_at,
                "maxMutations": lease.max_mutations,
            },
        }

    def _request_with_dpop(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        use_lease: bool = False,
        secret_values: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        device = self._device()
        key = self._device_key()
        url = self._url(path)
        headers: dict[str, str] = {}
        access_token: str | None = None
        if use_lease:
            lease = self._lease(device)
            access_token = lease.access_token
            headers["Authorization"] = f"DPoP {access_token}"
        headers["DPoP"] = key.dpop_proof(
            method=method, url=url, access_token=access_token
        )
        known_secrets = (*secret_values, *((access_token,) if access_token else ()))
        return self._request_json(
            method,
            path,
            body=body,
            headers=headers,
            secret_values=known_secrets,
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        secret_values: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        url = self._url(path)
        encoded = None
        request_headers = {
            "Accept": "application/json",
            "User-Agent": "virty-mcp/0.1.0",
            **dict(headers or {}),
        }
        if body is not None:
            encoded = json.dumps(
                body, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            request_headers["Content-Type"] = "application/json"

        status, response_headers, raw = self.transport.request(
            method=method,
            url=url,
            headers=request_headers,
            body=encoded,
            timeout=self.config.timeout_seconds,
            ssl_context=self._ssl_context,
        )
        content_type = next(
            (
                str(value)
                for name, value in response_headers.items()
                if str(name).lower() == "content-type"
            ),
            "",
        )
        try:
            decoded = json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AgentApiError(
                "Agent APIがJSONではない応答を返しました", status=status
            ) from exc
        if not isinstance(decoded, dict):
            raise AgentApiError("Agent API応答はJSON objectである必要があります", status=status)
        if not 200 <= status < 300:
            error = decoded.get("error") if isinstance(decoded.get("error"), dict) else {}
            raw_detail = decoded.get("detail")
            detail_error = raw_detail if isinstance(raw_detail, dict) else {}
            code = error.get("code") or detail_error.get("code") or decoded.get("code")
            detail = (
                error.get("message")
                or detail_error.get("message")
                or (raw_detail if isinstance(raw_detail, str) else None)
                or "Agent API requestが失敗しました"
            )
            if not isinstance(detail, str):
                detail = "Agent API requestが失敗しました"
            # 長いsecretを先に切るとprefixが漏れるため、全体をredactしてから表示長を制限する。
            safe_detail = str(
                redact_secrets(detail, secret_values=secret_values)
            )[:1000]
            raise AgentApiError(
                str(safe_detail),
                status=status,
                code=str(code) if code else None,
            )
        if raw and "json" not in content_type.lower():
            raise AgentApiError("Agent APIのContent-Typeがapplication/jsonではありません")
        return decoded

    def _device_key(self) -> DeviceKey:
        pem = self.repository.get_private_key_pem()
        if pem is None:
            raise AgentApiError("device鍵がありません。先にpairingを開始してください")
        try:
            return DeviceKey.from_pem(pem)
        except (TypeError, ValueError) as exc:
            raise AgentApiError("保存済みdevice鍵を読み込めません") from exc

    def _device(self) -> dict[str, Any]:
        device = self.repository.get_device()
        if device is None or not device.get("deviceId"):
            raise AgentApiError("承認済みdeviceがありません。pairingを完了してください")
        self._require_origin(device)
        return device

    def _lease(self, device: Mapping[str, Any]) -> LeaseCredential:
        lease = self.repository.get_lease()
        if lease is None:
            raise AgentApiError("有効な能力leaseがありません。先にleaseを取得してください")
        if lease.origin != self._origin or lease.device_id != str(device["deviceId"]):
            raise AgentApiError(
                "保存済みleaseは現在のVirty origin/deviceに束縛されていません。"
                "新しいleaseを取得してください"
            )
        try:
            expires_at = datetime.fromisoformat(lease.expires_at.replace("Z", "+00:00"))
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)
        except ValueError as exc:
            raise AgentApiError("保存済みleaseの有効期限が不正です") from exc
        if expires_at.astimezone(UTC) <= datetime.now(UTC):
            raise AgentApiError("能力leaseの有効期限が切れています")
        return lease

    def _require_origin(self, record: Mapping[str, Any]) -> None:
        if record.get("origin") != self._origin:
            raise AgentApiError(
                "保存済みdevice状態は現在のVirty originに束縛されていません。"
                "正しいprofile/URLへ戻すか、新しいprofileでpairingしてください"
            )

    def _url(self, path: str) -> str:
        base = self.config.base_url.rstrip("/") + "/"
        return urljoin(base, path.lstrip("/"))

    @staticmethod
    def _path_segment(value: Any) -> str:
        raw = str(value)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,254}", raw):
            raise AgentApiError("Agent API path IDの形式が不正です")
        return quote(raw, safe="")

    @staticmethod
    def _require_fields(value: dict[str, Any], *fields: str) -> None:
        missing = [field for field in fields if field not in value]
        if missing:
            raise AgentApiError(f"Agent API応答に必須fieldがありません: {', '.join(missing)}")

    @staticmethod
    def _without_secrets(value: dict[str, Any]) -> dict[str, Any]:
        redacted = redact_secrets(value)
        if not isinstance(redacted, dict):  # 入力型から到達しないが型を保証する
            raise TypeError("redacted Agent API response must be an object")
        return redacted
