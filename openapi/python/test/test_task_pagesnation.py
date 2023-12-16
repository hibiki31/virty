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

from virty_client.models.task_pagesnation import TaskPagesnation

class TestTaskPagesnation(unittest.TestCase):
    """TaskPagesnation unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> TaskPagesnation:
        """Test TaskPagesnation
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `TaskPagesnation`
        """
        model = TaskPagesnation()
        if include_optional:
            return TaskPagesnation(
                count = 56,
                data = [
                    virty_client.models.task.Task(
                        post_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        run_time = 1.337, 
                        start_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        update_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        user_id = '', 
                        status = '', 
                        resource = '', 
                        object = '', 
                        method = '', 
                        dependence_uuid = '', 
                        request = virty_client.models.request.Request(), 
                        result = virty_client.models.result.Result(), 
                        message = '', 
                        log = '', 
                        uuid = '', )
                    ]
            )
        else:
            return TaskPagesnation(
                count = 56,
                data = [
                    virty_client.models.task.Task(
                        post_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        run_time = 1.337, 
                        start_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        update_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        user_id = '', 
                        status = '', 
                        resource = '', 
                        object = '', 
                        method = '', 
                        dependence_uuid = '', 
                        request = virty_client.models.request.Request(), 
                        result = virty_client.models.result.Result(), 
                        message = '', 
                        log = '', 
                        uuid = '', )
                    ],
        )
        """

    def testTaskPagesnation(self):
        """Test TaskPagesnation"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
