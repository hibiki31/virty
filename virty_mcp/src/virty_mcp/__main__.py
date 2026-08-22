"""``virty-mcp`` のconsole entry point。"""

from __future__ import annotations

import sys

from .client import AgentApiClient, AgentApiConfig
from .credentials import KeyringCredentialStore, ProfileRepository
from .server import VirtyMcpServer


def main() -> None:
    """環境変数からhelperを構成し、stdio serverを開始する。"""

    try:
        config = AgentApiConfig.from_environment()
        credentials = KeyringCredentialStore(profile=config.profile)
        repository = ProfileRepository(credentials)
        client = AgentApiClient(config=config, repository=repository)
        VirtyMcpServer(client=client, repository=repository).run_stdio()
    except Exception as exc:  # stdoutはJSON-RPC専用のためstderrへ出す
        print(f"virty-mcpを開始できません: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
