# coding: utf-8

"""
    VirtyAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 4.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from virty_client.models.network_provider_for_create import NetworkProviderForCreate

class TestNetworkProviderForCreate(unittest.TestCase):
    """NetworkProviderForCreate unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> NetworkProviderForCreate:
        """Test NetworkProviderForCreate
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `NetworkProviderForCreate`
        """
        model = NetworkProviderForCreate()
        if include_optional:
            return NetworkProviderForCreate(
                name = '',
                dns_domain = '',
                network_address = '',
                network_prefix = '',
                gateway_address = '',
                dhcp_start = '',
                dhcp_end = '',
                network_node = ''
            )
        else:
            return NetworkProviderForCreate(
        )
        """

    def testNetworkProviderForCreate(self):
        """Test NetworkProviderForCreate"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
