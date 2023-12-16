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

from virty_client.models.image import Image

class TestImage(unittest.TestCase):
    """Image unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> Image:
        """Test Image
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Image`
        """
        model = Image()
        if include_optional:
            return Image(
                count = 56,
                data = [
                    virty_client.models.image_page.ImagePage(
                        name = '', 
                        storage_uuid = '', 
                        capacity = 56, 
                        storage = virty_client.models.storage_page.StoragePage(
                            name = '', 
                            uuid = '', 
                            status = 56, 
                            active = True, 
                            available = 56, 
                            capacity = 56, 
                            node_name = '', 
                            node = virty_client.models.node_page.NodePage(
                                name = '', 
                                description = '', 
                                domain = '', 
                                user_name = '', 
                                port = 56, 
                                core = 56, 
                                memory = 56, 
                                cpu_gen = '', 
                                os_like = '', 
                                os_name = '', 
                                os_version = '', 
                                status = 56, 
                                qemu_version = '', 
                                libvirt_version = '', 
                                roles = [
                                    virty_client.models.node_role.NodeRole(
                                        role_name = '', 
                                        extra_json = virty_client.models.extrajson.Extrajson(), )
                                    ], ), 
                            auto_start = True, 
                            path = '', 
                            meta_data = virty_client.models.storage_metadata.StorageMetadata(
                                rool = '', 
                                protocol = '', 
                                device_type = '', ), 
                            update_token = '', 
                            allocation_commit = 56, 
                            capacity_commit = 56, ), 
                        flavor = virty_client.models.flavor.Flavor(
                            count = 56, 
                            data = [
                                virty_client.models.flavor_page.FlavorPage(
                                    name = '', 
                                    os = '', 
                                    manual_url = '', 
                                    icon = '', 
                                    cloud_init_ready = True, 
                                    description = '', 
                                    id = 56, )
                                ], ), 
                        allocation = 56, 
                        path = '', 
                        update_token = '', 
                        domain = virty_client.models.image_domain.ImageDomain(
                            owner_user_id = '', 
                            issuance_id = 56, 
                            name = '', 
                            uuid = '', ), )
                    ]
            )
        else:
            return Image(
                count = 56,
                data = [
                    virty_client.models.image_page.ImagePage(
                        name = '', 
                        storage_uuid = '', 
                        capacity = 56, 
                        storage = virty_client.models.storage_page.StoragePage(
                            name = '', 
                            uuid = '', 
                            status = 56, 
                            active = True, 
                            available = 56, 
                            capacity = 56, 
                            node_name = '', 
                            node = virty_client.models.node_page.NodePage(
                                name = '', 
                                description = '', 
                                domain = '', 
                                user_name = '', 
                                port = 56, 
                                core = 56, 
                                memory = 56, 
                                cpu_gen = '', 
                                os_like = '', 
                                os_name = '', 
                                os_version = '', 
                                status = 56, 
                                qemu_version = '', 
                                libvirt_version = '', 
                                roles = [
                                    virty_client.models.node_role.NodeRole(
                                        role_name = '', 
                                        extra_json = virty_client.models.extrajson.Extrajson(), )
                                    ], ), 
                            auto_start = True, 
                            path = '', 
                            meta_data = virty_client.models.storage_metadata.StorageMetadata(
                                rool = '', 
                                protocol = '', 
                                device_type = '', ), 
                            update_token = '', 
                            allocation_commit = 56, 
                            capacity_commit = 56, ), 
                        flavor = virty_client.models.flavor.Flavor(
                            count = 56, 
                            data = [
                                virty_client.models.flavor_page.FlavorPage(
                                    name = '', 
                                    os = '', 
                                    manual_url = '', 
                                    icon = '', 
                                    cloud_init_ready = True, 
                                    description = '', 
                                    id = 56, )
                                ], ), 
                        allocation = 56, 
                        path = '', 
                        update_token = '', 
                        domain = virty_client.models.image_domain.ImageDomain(
                            owner_user_id = '', 
                            issuance_id = 56, 
                            name = '', 
                            uuid = '', ), )
                    ],
        )
        """

    def testImage(self):
        """Test Image"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
