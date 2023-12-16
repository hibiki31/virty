# coding: utf-8

"""
    VirtyAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 4.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from virty_client.api.networks_api import NetworksApi


class TestNetworksApi(unittest.TestCase):
    """NetworksApi unit test stubs"""

    def setUp(self) -> None:
        self.api = NetworksApi()

    def tearDown(self) -> None:
        pass

    def test_create_network_pool(self) -> None:
        """Test case for create_network_pool

        Post Api Networks Pools
        """
        pass

    def test_delete_network_pool(self) -> None:
        """Test case for delete_network_pool

        Delete Pools Uuid
        """
        pass

    def test_get_network(self) -> None:
        """Test case for get_network

        Get Api Networks Uuid
        """
        pass

    def test_get_network_pools(self) -> None:
        """Test case for get_network_pools

        Get Api Networks Pools
        """
        pass

    def test_get_networks(self) -> None:
        """Test case for get_networks

        Get Api Networks
        """
        pass

    def test_update_network_pool(self) -> None:
        """Test case for update_network_pool

        Patch Api Networks Pools
        """
        pass


if __name__ == '__main__':
    unittest.main()
