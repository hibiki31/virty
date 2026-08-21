"""pytest process終了後にも実行できるrun限定external resource cleanup。"""

import os

from tests.external.conftest import (
    _cleanup_marker,
    _load_infra_config,
    cleanup_resources,
    create_authenticated_client,
)


def main() -> None:
    marker = _cleanup_marker()
    if not marker.is_file():
        print("collision check完了前のためremote cleanupは実行しません")
        return
    env = _load_infra_config()
    run_prefix = os.environ["VIRTY_TEST_RUN_ID"]
    client = create_authenticated_client(env)
    key_response = client.post(
        "/api/nodes/key",
        json={"privateKey": env.key, "publicKey": env.pub},
    )
    key_response.raise_for_status()
    cleanup_resources(env, client, run_prefix)


if __name__ == "__main__":
    main()
