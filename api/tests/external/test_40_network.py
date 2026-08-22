def test_network_inventory(env, created_network) -> None:
    expected = {
        (network.name, server.name)
        for server in env.servers
        for network in env.networks
    }
    actual = {
        (network.name, network.node_name)
        for network in created_network.data
        if (network.name, network.node_name) in expected
    }
    if actual != expected:
        raise AssertionError(
            f"network inventory mismatch: count={len(actual.symmetric_difference(expected))}"
        )
