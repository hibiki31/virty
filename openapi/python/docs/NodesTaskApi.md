# virty_client.NodesTaskApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_node**](NodesTaskApi.md#create_node) | **POST** /api/tasks/nodes | Post Tasks Nodes
[**delete_node**](NodesTaskApi.md#delete_node) | **DELETE** /api/tasks/nodes/{name} | Delete Tasks Nodes Name
[**update_node_role**](NodesTaskApi.md#update_node_role) | **PATCH** /api/tasks/nodes/roles | Patch Api Node Role


# **create_node**
> List[Task] create_node(node_for_create=node_for_create)

Post Tasks Nodes

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.node_for_create import NodeForCreate
from virty_client.models.task import Task
from virty_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://virty-pr.hinagiku.me/api
# See configuration.py for a list of all supported configuration parameters.
configuration = virty_client.Configuration(
    host = "https://virty-pr.hinagiku.me/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with virty_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = virty_client.NodesTaskApi(api_client)
    node_for_create = virty_client.NodeForCreate() # NodeForCreate |  (optional)

    try:
        # Post Tasks Nodes
        api_response = api_instance.create_node(node_for_create=node_for_create)
        print("The response of NodesTaskApi->create_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NodesTaskApi->create_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_for_create** | [**NodeForCreate**](NodeForCreate.md)|  | [optional] 

### Return type

[**List[Task]**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_node**
> List[Task] delete_node(name)

Delete Tasks Nodes Name

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.task import Task
from virty_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://virty-pr.hinagiku.me/api
# See configuration.py for a list of all supported configuration parameters.
configuration = virty_client.Configuration(
    host = "https://virty-pr.hinagiku.me/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with virty_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = virty_client.NodesTaskApi(api_client)
    name = 'name_example' # str | 

    try:
        # Delete Tasks Nodes Name
        api_response = api_instance.delete_node(name)
        print("The response of NodesTaskApi->delete_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NodesTaskApi->delete_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**List[Task]**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_node_role**
> Task update_node_role(node_role_for_update)

Patch Api Node Role

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.node_role_for_update import NodeRoleForUpdate
from virty_client.models.task import Task
from virty_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://virty-pr.hinagiku.me/api
# See configuration.py for a list of all supported configuration parameters.
configuration = virty_client.Configuration(
    host = "https://virty-pr.hinagiku.me/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with virty_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = virty_client.NodesTaskApi(api_client)
    node_role_for_update = virty_client.NodeRoleForUpdate() # NodeRoleForUpdate | 

    try:
        # Patch Api Node Role
        api_response = api_instance.update_node_role(node_role_for_update)
        print("The response of NodesTaskApi->update_node_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NodesTaskApi->update_node_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_role_for_update** | [**NodeRoleForUpdate**](NodeRoleForUpdate.md)|  | 

### Return type

[**Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

