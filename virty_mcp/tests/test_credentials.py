from __future__ import annotations

from virty_mcp.credentials import _is_os_credential_backend


def _backend(module: str, name: str, priority: object = 5) -> object:
    backend_type = type(name, (), {"priority": priority})
    backend_type.__module__ = module
    return backend_type()


def test_only_standard_os_keyring_backends_are_accepted() -> None:
    assert _is_os_credential_backend(
        _backend("keyring.backends.SecretService", "Keyring")
    )
    assert _is_os_credential_backend(_backend("keyring.backends.macOS", "Keyring"))
    assert _is_os_credential_backend(
        _backend("keyring.backends.Windows", "WinVaultKeyring")
    )


def test_file_custom_chainer_and_disabled_keyring_backends_are_rejected() -> None:
    assert not _is_os_credential_backend(
        _backend("keyrings.alt.file", "PlaintextKeyring")
    )
    assert not _is_os_credential_backend(
        _backend("company.custom", "CredentialBackend")
    )
    assert not _is_os_credential_backend(
        _backend("keyring.backends.chainer", "ChainerBackend")
    )
    assert not _is_os_credential_backend(
        _backend("keyring.backends.fail", "Keyring", priority=0)
    )
