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

from virty_client.models.node_interface_ipv6_info import NodeInterfaceIpv6Info

class TestNodeInterfaceIpv6Info(unittest.TestCase):
    """NodeInterfaceIpv6Info unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> NodeInterfaceIpv6Info:
        """Test NodeInterfaceIpv6Info
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `NodeInterfaceIpv6Info`
        """
        model = NodeInterfaceIpv6Info()
        if include_optional:
            return NodeInterfaceIpv6Info(
                address = '',
                prefixlen = 56
            )
        else:
            return NodeInterfaceIpv6Info(
                address = '',
                prefixlen = 56,
        )
        """

    def testNodeInterfaceIpv6Info(self):
        """Test NodeInterfaceIpv6Info"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
