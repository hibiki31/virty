import shlex
from contextlib import ExitStack

import pytest

from tests.external.support.remote_inventory import remote_inventory_manager


def test_get_info(env, installed_sshkeys):
    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as manager:
            assert int(manager.get_node_cpu_core()) > 0
            assert int(manager.get_node_mem()) > 0
            assert manager.get_node_cpu_name().strip()
            release = manager.get_node_os_release()
            assert release["ID_LIKE"].strip()
            assert release["PRETTY_NAME"].strip()
            assert release["VERSION_ID"].strip()
            assert manager.get_node_qemu_version().strip()
            assert manager.get_node_libvirt_version().strip()


def test_get_copy_node_to_node(env, installed_sshkeys, run_prefix):
    if len(env.servers) < 2:
        pytest.skip("node間copyには2台以上の専用nodeが必要です")

    source_path = f"/tmp/{run_prefix}-virty-copy-source"
    destination_path = f"/tmp/{run_prefix}-virty-copy-destination"
    quoted_source = shlex.quote(source_path)
    quoted_destination = shlex.quote(destination_path)
    transfers: list[tuple[int, int, str]] = []
    with ExitStack() as stack:
        managers = [
            stack.enter_context(
                remote_inventory_manager(
                    user=server.username,
                    domain=server.domain,
                    server_index=server_index,
                )
            )
            for server_index, server in enumerate(env.servers)
        ]
        for source_index, source in enumerate(managers):
            destination_index = (source_index + 1) % len(managers)
            destination = managers[destination_index]
            source.run_cmd(
                f"dd if=/dev/zero of={quoted_source} bs=1M count=1 status=none "
                f"&& printf 'source-{source_index:08d}' "
                f"| dd of={quoted_source} bs=1 conv=notrunc status=none"
            )
            destination.run_cmd(f"rm -f -- {quoted_destination}")
            destination.run_cmd(f"test ! -e {quoted_destination}")
            source.scp_node_to_node(
                src_node=source,
                dst_node=destination,
                src_path=source_path,
                dst_path=destination_path,
            )
            source_hash = source.run_cmd(
                f"sha256sum -- {quoted_source} | awk '{{print $1}}'"
            ).stdout.strip()
            destination_hash = destination.run_cmd(
                f"sha256sum -- {quoted_destination} | awk '{{print $1}}'"
            ).stdout.strip()
            destination_size = int(
                destination.run_cmd(
                    f"stat -Lc %s -- {quoted_destination}"
                ).stdout.strip()
            )
            assert source_hash == destination_hash
            assert destination_size == 1024**2
            transfers.append((source_index, destination_index, source_hash))

        assert {source for source, _destination, _digest in transfers} == set(
            range(len(managers))
        )
        assert {destination for _source, destination, _digest in transfers} == set(
            range(len(managers))
        )
        assert len({digest for _source, _destination, digest in transfers}) == len(
            managers
        )
