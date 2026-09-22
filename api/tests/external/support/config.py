"""専用lab設定の厳格な読込とrun固有名の生成。"""

from __future__ import annotations

import json
import re
from ipaddress import ip_address, ip_network
from io import StringIO
from pathlib import Path, PurePosixPath
from typing import Any, Self
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


RUN_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{5,31}")
RESOURCE_NAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,31}")
LAB_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}")
MAX_DERIVED_NAME_LENGTH = 64
DOCUMENTATION_NETWORKS = (
    ip_network("192.0.2.0/24"),
    ip_network("198.51.100.0/24"),
    ip_network("203.0.113.0/24"),
)
PLACEHOLDER_FRAGMENTS = (
    "__REPLACE_MANUALLY_",
    "replace-me",
    "replace-with-dedicated-lab-id",
)


class InfraConfigError(ValueError):
    """設定本文を含まない、専用lab設定の検証error。"""


class StrictConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)

    def __repr_args__(self) -> list[tuple[str | None, Any]]:
        # pytestのfixture表示や例外の補助表示にもlab設定値を残さない。
        return [("redacted", True)]


def _validate_resource_name(value: str) -> str:
    if RESOURCE_NAME_PATTERN.fullmatch(value) is None:
        raise ValueError("base nameの形式が不正です")
    if any(fragment in value for fragment in PLACEHOLDER_FRAGMENTS):
        raise ValueError("placeholderを使用できません")
    return value


def _validate_nonsecret_identifier(value: str) -> str:
    if not value or any(character.isspace() for character in value):
        raise ValueError("空文字または空白を使用できません")
    if any(fragment in value for fragment in PLACEHOLDER_FRAGMENTS):
        raise ValueError("placeholderを使用できません")
    return value


def _validate_password(value: str) -> str:
    if not 8 <= len(value) <= 128 or any(character.isspace() for character in value):
        raise ValueError("password policyを満たしません")
    categories = (
        re.search(r"[a-z]", value),
        re.search(r"[A-Z]", value),
        re.search(r"\d", value),
        re.search(r"[^A-Za-z0-9]", value),
    )
    if not all(categories) or any(fragment in value for fragment in PLACEHOLDER_FRAGMENTS):
        raise ValueError("password policyを満たしません")
    return value


def _validate_server_address(value: str) -> str:
    value = _validate_nonsecret_identifier(value)
    if value.endswith(".invalid"):
        raise ValueError("documentation用addressを使用できません")
    try:
        address = ip_address(value)
    except ValueError:
        return value
    if any(address in network for network in DOCUMENTATION_NETWORKS):
        raise ValueError("documentation用addressを使用できません")
    return value


def _validate_storage_path(value: str) -> str:
    if not value or any(character.isspace() for character in value):
        raise ValueError("storage pathに空白を使用できません")
    raw_parts = value.split("/")
    if any(part in {".", ".."} for part in raw_parts):
        raise ValueError("storage pathに'.'または'..'を使用できません")
    if any(part == "" for part in raw_parts[1:]):
        raise ValueError("storage pathは正規化してください")
    path = PurePosixPath(value)
    if not path.is_absolute() or path == PurePosixPath("/") or str(path) != value:
        raise ValueError("storage pathは正規化済み絶対pathで指定してください")
    if any(fragment in value for fragment in PLACEHOLDER_FRAGMENTS):
        raise ValueError("placeholderを使用できません")
    return value


def _validate_download_url(value: str) -> str:
    if any(character.isspace() for character in value):
        raise ValueError("download URLに空白を使用できません")
    parsed = urlparse(value)
    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise ValueError("download URLのportが不正です") from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or not PurePosixPath(parsed.path).name
        or parsed.hostname.endswith(".invalid")
        or parsed_port is not None and not 1 <= parsed_port <= 65535
    ):
        raise ValueError("認証情報を含まないfile付きHTTP(S) URLが必要です")
    if any(fragment in value for fragment in PLACEHOLDER_FRAGMENTS):
        raise ValueError("placeholderを使用できません")
    return value


def _validate_key_pair(private_key: str, public_key: str) -> None:
    """秘密値を例外文へ含めず、対応するRSA/Ed25519 key pairだけを許可する。"""

    from paramiko import Ed25519Key, RSAKey, SSHException

    parsed_private = None
    for key_class in (Ed25519Key, RSAKey):
        try:
            parsed_private = key_class.from_private_key(StringIO(private_key))
            break
        except (SSHException, ValueError):
            continue
    if parsed_private is None:
        raise ValueError("RSAまたはEd25519 OpenSSH秘密鍵が必要です")

    public_parts = public_key.split()
    if len(public_parts) < 2 or public_parts[0] not in {"ssh-ed25519", "ssh-rsa"}:
        raise ValueError("RSAまたはEd25519 OpenSSH公開鍵が必要です")
    if (
        public_parts[0] != parsed_private.get_name()
        or public_parts[1] != parsed_private.get_base64()
    ):
        raise ValueError("keyとpubが同じkey pairではありません")


class User(StrictConfigModel):
    username: str
    password: str
    publickey: str

    _username = field_validator("username")(_validate_resource_name)
    _password = field_validator("password")(_validate_password)


class Project(StrictConfigModel):
    name: str

    _name = field_validator("name")(_validate_resource_name)


class Server(StrictConfigModel):
    name: str
    domain: str
    username: str

    _name = field_validator("name")(_validate_resource_name)
    _domain = field_validator("domain")(_validate_server_address)
    _username = field_validator("username")(_validate_nonsecret_identifier)


class Storage(StrictConfigModel):
    name: str
    path: str

    _name = field_validator("name")(_validate_resource_name)
    _path = field_validator("path")(_validate_storage_path)


class Networks(StrictConfigModel):
    name: str
    type: str
    octet: int = Field(ge=0, le=255)

    _name = field_validator("name")(_validate_resource_name)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value != "nat":
            raise ValueError("external suiteではnetwork typeをnatに限定します")
        return value

    @model_validator(mode="after")
    def validate_suffix(self) -> Self:
        if not self.name.endswith("test-nat"):
            raise ValueError("network名は'test-nat'で終わる必要があります")
        return self


class VM(StrictConfigModel):
    name: str
    image: str
    network: str

    _name = field_validator("name")(_validate_resource_name)
    _image = field_validator("image")(_validate_nonsecret_identifier)
    _network = field_validator("network")(_validate_nonsecret_identifier)


class EnvConfig(StrictConfigModel):
    allow_destructive: bool
    lab_id: str
    username: str
    password: str
    users: list[User] = Field(min_length=1)
    projects: list[Project] = Field(min_length=1)
    key: str
    pub: str
    servers: list[Server] = Field(min_length=1)
    storages: list[Storage] = Field(min_length=1)
    networks: list[Networks] = Field(min_length=1)
    vms: list[VM] = Field(min_length=1)
    image_url: str
    iso_url: str

    _username = field_validator("username")(_validate_resource_name)
    _password = field_validator("password")(_validate_password)
    _image_url = field_validator("image_url")(_validate_download_url)
    _iso_url = field_validator("iso_url")(_validate_download_url)

    @field_validator("lab_id")
    @classmethod
    def validate_lab_id(cls, value: str) -> str:
        if LAB_ID_PATTERN.fullmatch(value) is None:
            raise ValueError("lab_idの形式が不正です")
        if any(fragment in value for fragment in PLACEHOLDER_FRAGMENTS):
            raise ValueError("placeholderを使用できません")
        return value

    @model_validator(mode="after")
    def validate_safety_contract(self) -> Self:
        if self.allow_destructive is not True:
            raise ValueError("allow_destructive=trueの専用lab設定が必要です")

        collections: dict[str, list[Any]] = {
            "servers": self.servers,
            "storages": self.storages,
            "networks": self.networks,
            "vms": self.vms,
            "users": self.users,
            "projects": self.projects,
        }
        for label, resources in collections.items():
            names = [
                resource.name if hasattr(resource, "name") else resource.username
                for resource in resources
            ]
            if len(names) != len(set(names)):
                raise ValueError(f"{label}の名前は重複できません")

        if len({server.domain for server in self.servers}) != len(self.servers):
            raise ValueError("serversの接続先は重複できません")
        if len({storage.path for storage in self.storages}) != len(self.storages):
            raise ValueError("storage pathは重複できません")
        if len({network.octet for network in self.networks}) != len(self.networks):
            raise ValueError("network octetは重複できません")
        if self.username in {user.username for user in self.users}:
            raise ValueError("admin usernameとtest userは重複できません")
        network_names = {network.name for network in self.networks}
        if any(vm.network not in network_names for vm in self.vms):
            raise ValueError("VM networkはnetworksのexact nameを参照してください")

        for suffix in ("test-cloud", "test-iso", "test-img"):
            if sum(storage.name.endswith(suffix) for storage in self.storages) != 1:
                raise ValueError(f"末尾{suffix!r}のstorageを1件だけ指定してください")

        _validate_key_pair(self.key, self.pub)
        return self


def _safe_validation_summary(exc: ValidationError) -> str:
    fields: list[str] = []
    for error in exc.errors(include_url=False, include_context=False, include_input=False):
        location = ".".join(str(part) for part in error.get("loc", ())) or "root"
        error_type = str(error.get("type", "invalid"))
        reason = str(error.get("msg", "invalid"))
        fields.append(f"{location} ({error_type}: {reason})")
    return ", ".join(fields[:12]) or "root (invalid)"


def parse_infra_config_json(raw_json: str) -> EnvConfig:
    """JSON本文を例外へ含めずに検証する。"""

    try:
        payload = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError):
        raise InfraConfigError("専用lab設定のJSON形式が不正です") from None
    try:
        return EnvConfig.model_validate(payload)
    except ValidationError as exc:
        raise InfraConfigError(
            "専用lab設定の検証に失敗しました: " + _safe_validation_summary(exc)
        ) from None


def load_infra_config_file(path: str | Path) -> EnvConfig:
    config_path = Path(path)
    try:
        raw_json = config_path.read_text(encoding="utf-8")
    except OSError:
        raise InfraConfigError("専用lab設定を読み取れません") from None
    return parse_infra_config_json(raw_json)


def validate_infra_config(config: EnvConfig) -> None:
    """互換入口。model生成済みなら全validatorを通過している。"""

    if not isinstance(config, EnvConfig):
        raise InfraConfigError("専用lab設定modelが不正です")


def validate_run_id(run_id: str) -> str:
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise InfraConfigError("run IDの形式が不正です")
    return run_id


def derive_resource_name(run_id: str, *base_names: str) -> str:
    """run IDを一度だけ含む64文字以下のexact resource名を返す。"""

    validate_run_id(run_id)
    prefix = f"{run_id}-"
    normalized = [name.removeprefix(prefix) for name in base_names]
    derived = "-".join((run_id, *normalized))
    if len(derived) > MAX_DERIVED_NAME_LENGTH:
        raise InfraConfigError("run固有resource名が64文字を超えます")
    return derived


def apply_run_prefix(config: EnvConfig, run_id: str) -> EnvConfig:
    """入力modelを変更せず、run固有の資源名とpathを返す。"""

    validate_run_id(run_id)
    simple_names = [
        config.username,
        *(user.username for user in config.users),
        *(project.name for project in config.projects),
        *(server.name for server in config.servers),
        *(storage.name for storage in config.storages),
        *(network.name for network in config.networks),
        *(vm.name for vm in config.vms),
    ]
    for name in simple_names:
        derive_resource_name(run_id, name)
    for server in config.servers:
        for vm in config.vms:
            derive_resource_name(run_id, vm.name, server.name)
    for storage in config.storages:
        derive_resource_name(run_id, PurePosixPath(storage.path).name)
    derived_vms = {
        derive_resource_name(run_id, vm.name, server.name)
        for server in config.servers
        for vm in config.vms
    }
    if len(derived_vms) != len(config.servers) * len(config.vms):
        raise InfraConfigError("run固有VM名が重複します")

    prefixed = config.model_copy(deep=True)
    prefixed.username = derive_resource_name(run_id, prefixed.username)
    for project in prefixed.projects:
        project.name = derive_resource_name(run_id, project.name)
    for server in prefixed.servers:
        server.name = derive_resource_name(run_id, server.name)
    for storage in prefixed.storages:
        storage.name = derive_resource_name(run_id, storage.name)
    for network in prefixed.networks:
        network.name = derive_resource_name(run_id, network.name)
    for vm in prefixed.vms:
        vm.name = derive_resource_name(run_id, vm.name)
        vm.network = derive_resource_name(run_id, vm.network)
    for user in prefixed.users:
        user.username = derive_resource_name(run_id, user.username)
    for storage in prefixed.storages:
        path = PurePosixPath(storage.path)
        storage.path = str(
            path.with_name(derive_resource_name(run_id, path.name))
        )
    return prefixed
