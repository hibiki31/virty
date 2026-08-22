"""cleanup後にmanifest全targetの不在を独立inventoryするCLI。"""

from __future__ import annotations

import logging
import shlex
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from domain.models import DomainModel
from mixin.database import SessionLocal
from network.models import NetworkModel
from project.models import ProjectModel
from sqlalchemy import and_, or_
from storage.models import StorageModel
from tests.external.preflight import _load_base_config
from tests.external.support.config import apply_run_prefix
from tests.external.support.manifest import (
    CleanupPlanner,
    infra_project_id,
    load_manifest,
    manifest_path,
)
from tests.external.support.remote_inventory import logical_libvirt_name
from user.models import UserModel


class CleanupVerificationError(RuntimeError):
    """config由来の値を含まないinventory error。"""


@contextmanager
def _muted_paramiko_logger() -> Iterator[None]:
    logger = logging.getLogger("module.paramikolib")
    previous = logger.disabled
    logger.disabled = True
    try:
        yield
    finally:
        logger.disabled = previous


def _verify_database_absence(planner: CleanupPlanner) -> int:
    from node.models import NodeModel

    local_model_by_kind = {
        "project": (ProjectModel, ProjectModel.name),
        "node": (NodeModel, NodeModel.name),
        "user": (UserModel, UserModel.username),
    }
    node_model_by_kind = {
        "vm": DomainModel,
        "network": NetworkModel,
        "storage": StorageModel,
    }
    run_owned_fields = {
        "project": (ProjectModel, ProjectModel.name),
        "node": (NodeModel, NodeModel.name),
        "user": (UserModel, UserModel.username),
        "vm": (DomainModel, DomainModel.name),
        "network": (NetworkModel, NetworkModel.name),
        "storage": (StorageModel, StorageModel.name),
    }
    checked = 0
    try:
        with SessionLocal() as db:
            for entry in planner.all_entries():
                if entry.kind in local_model_by_kind:
                    model, field = local_model_by_kind[entry.kind]
                    remains = db.query(model).filter(field == entry.name).count()
                elif entry.kind in node_model_by_kind:
                    model = node_model_by_kind[entry.kind]
                    target = and_(
                        model.name == entry.name,
                        model.node_name == entry.node,
                    )
                    if entry.resource_uuid is not None:
                        target = or_(target, model.uuid == entry.resource_uuid)
                    remains = db.query(model).filter(target).count()
                else:
                    continue
                if remains != 0:
                    raise CleanupVerificationError(
                        f"cleanup inventory remains: kind={entry.kind} count={remains}"
                    )
                checked += 1
            prefix = f"{planner.manifest.run_id}-%"
            for kind, (model, field) in run_owned_fields.items():
                remains = db.query(model).filter(field.like(prefix)).count()
                if remains != 0:
                    raise CleanupVerificationError(
                        f"cleanup run inventory remains: kind={kind} count={remains}"
                    )
                checked += 1
    except CleanupVerificationError:
        raise
    except Exception:
        raise CleanupVerificationError("cleanup DB inventory failed") from None
    return checked


def _verify_existing_ssh_key_files(home: Path | None = None) -> None:
    """read-only verifierではpreflightが配置したkey pairの存在とmodeだけを検査する。"""

    ssh_directory = (home or Path.home()) / ".ssh"
    pairs = [
        (ssh_directory / "id_rsa", ssh_directory / "id_rsa.pub"),
        (ssh_directory / "id_ed25519", ssh_directory / "id_ed25519.pub"),
    ]
    valid_pairs = []
    try:
        if (
            not ssh_directory.is_dir()
            or ssh_directory.is_symlink()
            or stat.S_IMODE(ssh_directory.stat().st_mode) != 0o700
        ):
            raise CleanupVerificationError(
                "cleanup SSH key inventory failed: count=1"
            )
        for private_path, public_path in pairs:
            if not private_path.exists() and not public_path.exists():
                continue
            if (
                not private_path.is_file()
                or not public_path.is_file()
                or private_path.is_symlink()
                or public_path.is_symlink()
                or stat.S_IMODE(private_path.stat().st_mode) != 0o600
                or stat.S_IMODE(public_path.stat().st_mode) != 0o600
            ):
                raise CleanupVerificationError(
                    "cleanup SSH key inventory failed: count=1"
                )
            valid_pairs.append((private_path, public_path))
    except CleanupVerificationError:
        raise
    except OSError:
        raise CleanupVerificationError("cleanup SSH key inventory failed: count=1") from None
    if len(valid_pairs) != 1:
        raise CleanupVerificationError(
            f"cleanup SSH key inventory failed: count={len(valid_pairs)}"
        )


def _verify_remote_absence(env, planner: CleanupPlanner) -> int:
    from module.paramikolib import ParamikoManager

    checked = 0
    entries_by_node = {
        server.name: [
            entry for entry in planner.all_entries() if entry.node == server.name
        ]
        for server in env.servers
    }
    for server_index, server in enumerate(env.servers):
        manager = None
        try:
            with _muted_paramiko_logger():
                manager = ParamikoManager(
                    user=server.username,
                    domain=server.domain,
                    port=22,
                    connect_timeout=10,
                    operation_timeout=60,
                )
                names = {
                    "vm": {
                        logical_libvirt_name("vm", raw_name)
                        for raw_name in manager.run_cmd(
                            "virsh list --all --name"
                        ).stdout.splitlines()
                    },
                    "network": set(
                        manager.run_cmd("virsh net-list --all --name").stdout.splitlines()
                    ),
                    "storage": set(
                        manager.run_cmd("virsh pool-list --all --name").stdout.splitlines()
                    ),
                }
                uuids = {
                    "vm": set(manager.run_cmd("virsh list --all --uuid").stdout.splitlines()),
                    "network": set(
                        manager.run_cmd("virsh net-list --all --uuid").stdout.splitlines()
                    ),
                    "storage": set(
                        manager.run_cmd("virsh pool-list --all --uuid").stdout.splitlines()
                    ),
                }
                for entry in entries_by_node[server.name]:
                    if entry.kind in names:
                        if entry.name in names[entry.kind] or (
                            entry.resource_uuid is not None
                            and entry.resource_uuid in uuids[entry.kind]
                        ):
                            raise CleanupVerificationError(
                                "cleanup inventory remains: "
                                f"kind={entry.kind} server_index={server_index} count=1"
                            )
                        checked += 1
                    elif entry.kind == "remote_path":
                        result = manager.run_cmd(
                            "if test -e "
                            f"{shlex.quote(entry.path or '')}; then printf present; fi"
                        )
                        if result.stdout == "present":
                            raise CleanupVerificationError(
                                "cleanup inventory remains: "
                                f"kind=remote_path server_index={server_index} count=1"
                            )
                        checked += 1
                prefix = f"{planner.manifest.run_id}-"
                for kind, inventory in names.items():
                    remains = sum(name.startswith(prefix) for name in inventory)
                    if remains:
                        raise CleanupVerificationError(
                            "cleanup run inventory remains: "
                            f"kind={kind} server_index={server_index} count={remains}"
                        )
                    checked += 1
        except CleanupVerificationError:
            raise
        except Exception:
            raise CleanupVerificationError(
                f"cleanup remote inventory failed: server_index={server_index}"
            ) from None
        finally:
            if manager is not None:
                try:
                    with _muted_paramiko_logger():
                        manager.close()
                except Exception:
                    pass
    return checked


def verify_cleanup() -> int:
    config, run_id = _load_base_config()
    env = apply_run_prefix(config, run_id)
    _verify_existing_ssh_key_files()
    manifest = load_manifest(
        manifest_path(),
        expected_run_id=run_id,
        expected_lab_id=config.lab_id,
        expected_project_id=infra_project_id(),
    )
    planner = CleanupPlanner(manifest)
    return _verify_database_absence(planner) + _verify_remote_absence(env, planner)


def main() -> None:
    try:
        checked = verify_cleanup()
    except Exception as exc:
        if isinstance(exc, CleanupVerificationError):
            message = str(exc)
        else:
            message = "cleanup verification failed"
        raise SystemExit(message) from None
    print(f"cleanup verification ok resources={checked}")


if __name__ == "__main__":
    main()
