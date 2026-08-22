import json
import traceback
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tests.external.support.config import (
    EnvConfig,
    InfraConfigError,
    apply_run_prefix,
    derive_resource_name,
    parse_infra_config_json,
)


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


def _key_pair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_value = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public_value = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    ).decode("ascii")
    return private_value, public_value


def _valid_payload() -> dict[str, Any]:
    private_key, public_key = _key_pair()
    return {
        "allow_destructive": True,
        "lab_id": "dedicated-lab-1",
        "username": "admin",
        "password": "Virty-Test_2026!",
        "users": [
            {
                "username": "test-user",
                "password": "Virty-User_2026!",
                "publickey": "__UNUSED_BY_CURRENT_SUITE__",
            }
        ],
        "projects": [{"name": "test-project"}],
        "key": private_key,
        "pub": public_key,
        "servers": [
            {
                "name": "test-node",
                "domain": "node.lab.example.test",
                "username": "lab-user",
            }
        ],
        "storages": [
            {"name": "test-cloud", "path": "/var/lib/libvirt/virty-test/cloud"},
            {"name": "test-iso", "path": "/var/lib/libvirt/virty-test/iso"},
            {"name": "test-img", "path": "/var/lib/libvirt/virty-test/images"},
        ],
        "networks": [{"name": "test-nat", "type": "nat", "octet": 240}],
        "vms": [{"name": "test-vm", "image": "unused", "network": "test-nat"}],
        "image_url": "https://downloads.example.test/cloud-image.qcow2",
        "iso_url": "https://downloads.example.test/installer.iso",
    }


def _parse_payload(payload: dict[str, Any]) -> EnvConfig:
    return parse_infra_config_json(json.dumps(payload))


def test_valid_config_and_run_prefix_do_not_mutate_input() -> None:
    config = _parse_payload(_valid_payload())
    original = config.model_dump()

    prefixed = apply_run_prefix(config, "run-123456")

    assert config.model_dump() == original
    assert prefixed.username == "run-123456-admin"
    assert prefixed.servers[0].name == "run-123456-test-node"
    assert prefixed.storages[0].path.endswith("/run-123456-cloud")
    assert prefixed.vms[0].network == "run-123456-test-nat"
    assert derive_resource_name(
        "run-123456",
        prefixed.vms[0].name,
        prefixed.servers[0].name,
    ) == "run-123456-test-vm-test-node"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload.update(allow_destructive="true"),
        lambda payload: payload.update(unexpected="value"),
        lambda payload: payload.update(username="UPPER_CASE"),
        lambda payload: payload.update(password="weak-password"),
        lambda payload: payload["storages"][0].update(path="/var/lib/../unsafe"),
        lambda payload: payload["networks"][0].update(type="bridge"),
        lambda payload: payload["networks"][0].update(octet=256),
        lambda payload: payload.update(
            image_url="https://credential@downloads.example.test/image.qcow2"
        ),
        lambda payload: payload.update(
            iso_url="https://downloads.example.test/installer.iso?token=value"
        ),
        lambda payload: payload["servers"][0].update(domain="192.0.2.10"),
        lambda payload: payload["users"][0].update(username=payload["username"]),
        lambda payload: payload["vms"][0].update(network="missing-network"),
    ],
)
def test_invalid_config_is_rejected(mutation) -> None:
    payload = _valid_payload()
    mutation(payload)

    with pytest.raises(InfraConfigError):
        _parse_payload(payload)


def test_duplicate_paths_and_octets_are_rejected() -> None:
    payload = _valid_payload()
    payload["storages"].append(
        {"name": "other-test-cloud", "path": "/var/lib/libvirt/virty-test/cloud"}
    )
    payload["networks"].append(
        {"name": "other-test-nat", "type": "nat", "octet": 240}
    )

    with pytest.raises(InfraConfigError):
        _parse_payload(payload)


def test_mismatched_key_pair_is_rejected_without_value_in_traceback() -> None:
    payload = _valid_payload()
    _private, different_public = _key_pair()
    payload["pub"] = different_public
    secret_seed = str(payload["key"])

    with pytest.raises(InfraConfigError) as caught:
        _parse_payload(payload)

    rendered = "".join(traceback.format_exception(caught.value))
    assert secret_seed not in rendered
    assert different_public not in rendered
    assert caught.value.__cause__ is None


def test_validation_error_does_not_expose_seeded_secret() -> None:
    payload = _valid_payload()
    secret_seed = "Seeded-Secret-Value_123!"
    payload["password"] = [secret_seed]

    with pytest.raises(InfraConfigError) as caught:
        _parse_payload(payload)

    rendered = "".join(traceback.format_exception(caught.value))
    assert secret_seed not in str(caught.value)
    assert secret_seed not in rendered
    assert "password" in str(caught.value)
    assert caught.value.__cause__ is None


def test_derived_name_length_boundary_fails_closed() -> None:
    assert len(derive_resource_name("run-123456", "a" * 53)) == 64
    with pytest.raises(InfraConfigError, match="64文字"):
        derive_resource_name("run-123456", "a" * 54)

    payload = _valid_payload()
    payload["vms"][0]["name"] = "v" * 32
    payload["servers"][0]["name"] = "n" * 32
    config = _parse_payload(payload)
    original = config.model_dump()
    with pytest.raises(InfraConfigError, match="64文字"):
        apply_run_prefix(config, "run-123456")
    assert config.model_dump() == original

    payload = _valid_payload()
    payload["storages"][0]["path"] = "/var/lib/libvirt/" + "s" * 54
    config = _parse_payload(payload)
    original = config.model_dump()
    with pytest.raises(InfraConfigError, match="64文字"):
        apply_run_prefix(config, "run-123456")
    assert config.model_dump() == original
