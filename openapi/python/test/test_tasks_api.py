# coding: utf-8

"""
    VirtyAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 4.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from virty_client.api.tasks_api import TasksApi


class TestTasksApi(unittest.TestCase):
    """TasksApi unit test stubs"""

    def setUp(self) -> None:
        self.api = TasksApi()

    def tearDown(self) -> None:
        pass

    def test_delete_tasks(self) -> None:
        """Test case for delete_tasks

        Delete Tasks
        """
        pass

    def test_get_incomplete_tasks(self) -> None:
        """Test case for get_incomplete_tasks

        Get Tasks Incomplete
        """
        pass

    def test_get_task(self) -> None:
        """Test case for get_task

        Get Tasks
        """
        pass

    def test_get_tasks(self) -> None:
        """Test case for get_tasks

        Get Tasks
        """
        pass


if __name__ == '__main__':
    unittest.main()
