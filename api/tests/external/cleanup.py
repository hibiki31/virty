"""pytest process終了後にも実行できるrun限定external resource cleanup。"""

import os
import stat
import sys
from collections.abc import Sequence

from tests.external.conftest import (
    _cleanup_marker,
    _load_infra_config,
    cleanup_resources,
    create_authenticated_client,
)
from tests.external.support.config import EnvConfig
from tests.external.support.manifest import (
    infra_project_id,
    load_manifest,
    manifest_path,
)


class CleanupGuardError(RuntimeError):
    """marker/manifest本文を含めないmanual cleanup guard error。"""


def _validate_cleanup_guard(env: EnvConfig, run_prefix: str) -> None:
    marker = _cleanup_marker()
    try:
        if (
            not marker.is_file()
            or marker.is_symlink()
            or stat.S_IMODE(marker.stat().st_mode) != 0o600
            or marker.read_text(encoding="utf-8").strip() != run_prefix
        ):
            raise CleanupGuardError("cleanup marker identityが一致しません")
    except CleanupGuardError:
        raise
    except OSError:
        raise CleanupGuardError("cleanup markerを安全に読み取れません") from None
    load_manifest(
        manifest_path(),
        expected_run_id=run_prefix,
        expected_lab_id=env.lab_id,
        expected_project_id=infra_project_id(),
    )


def _load_guarded_context() -> tuple[EnvConfig, str]:
    env = _load_infra_config()
    run_prefix = os.environ["VIRTY_TEST_RUN_ID"]
    _validate_cleanup_guard(env, run_prefix)
    return env, run_prefix


def guard_only() -> None:
    """DB・SSH・networkへ接続せずcleanup identityだけを検証する。"""

    try:
        _load_guarded_context()
    except KeyboardInterrupt:
        raise
    except BaseException:
        raise SystemExit(
            "external cleanup guard failed: kind=validation count=1"
        ) from None


def main() -> None:
    try:
        # auth setup/SSH key POSTを含む全mutationより先にidentityを固定する。
        env, run_prefix = _load_guarded_context()
        client = create_authenticated_client(env)
        key_response = client.post(
            "/api/nodes/key",
            json={"privateKey": env.key, "publicKey": env.pub},
        )
        key_response.raise_for_status()
        cleanup_resources(env, client, run_prefix)
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise SystemExit("external cleanup failed: kind=setup count=1") from None


def cli(argv: Sequence[str] | None = None) -> None:
    """秘密値や不正な引数本文を診断へ含めないcleanup CLI。"""

    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["guard"]:
        guard_only()
        return
    if args:
        raise SystemExit("external cleanup failed: kind=usage count=1") from None
    main()


if __name__ == "__main__":
    cli()
