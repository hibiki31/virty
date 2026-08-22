import os
import stat
import threading
import time
from pathlib import Path

import node.router as node_router
import pytest


def test_ssh_key_install_is_serialized_across_callers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(node_router, "SSH_DIRECTORY", tmp_path)
    monkeypatch.setattr(node_router, "SSH_KEY_NAMES", ("id_ed25519",))

    original_replace = os.replace
    counter_lock = threading.Lock()
    active_replaces = 0
    maximum_active_replaces = 0

    def delayed_replace(source: str | Path, destination: str | Path) -> None:
        nonlocal active_replaces, maximum_active_replaces
        with counter_lock:
            active_replaces += 1
            maximum_active_replaces = max(maximum_active_replaces, active_replaces)
        try:
            time.sleep(0.05)
            original_replace(source, destination)
        finally:
            with counter_lock:
                active_replaces -= 1

    monkeypatch.setattr(node_router.os, "replace", delayed_replace)
    start = threading.Barrier(3)
    errors: list[BaseException] = []

    def install(marker: str) -> None:
        try:
            start.wait()
            node_router._install_ssh_key_pair(
                key_name="id_ed25519",
                private_key=f"private-{marker}",
                public_key=f"public-{marker}",
            )
        except BaseException as exc:  # pragma: no cover - failure is asserted below
            errors.append(exc)

    threads = [
        threading.Thread(target=install, args=(marker,))
        for marker in ("a", "b")
    ]
    for thread in threads:
        thread.start()
    start.wait()
    for thread in threads:
        thread.join(timeout=5)

    assert not errors
    assert all(not thread.is_alive() for thread in threads)
    assert maximum_active_replaces == 1
    private_marker = (tmp_path / "id_ed25519").read_text().strip().removeprefix(
        "private-"
    )
    public_marker = (tmp_path / "id_ed25519.pub").read_text().strip().removeprefix(
        "public-"
    )
    assert private_marker == public_marker
    lock_mode = stat.S_IMODE((tmp_path / ".virty-key-install.lock").stat().st_mode)
    assert lock_mode == 0o600
