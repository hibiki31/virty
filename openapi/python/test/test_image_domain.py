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

from virty_client.models.image_domain import ImageDomain

class TestImageDomain(unittest.TestCase):
    """ImageDomain unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ImageDomain:
        """Test ImageDomain
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ImageDomain`
        """
        model = ImageDomain()
        if include_optional:
            return ImageDomain(
                owner_user_id = '',
                issuance_id = 56,
                name = '',
                uuid = ''
            )
        else:
            return ImageDomain(
                name = '',
                uuid = '',
        )
        """

    def testImageDomain(self):
        """Test ImageDomain"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
