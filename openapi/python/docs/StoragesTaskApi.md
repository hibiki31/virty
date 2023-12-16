# virty_client.StoragesTaskApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_storage**](StoragesTaskApi.md#create_storage) | **POST** /api/tasks/storages | Post Api Storage
[**delete_storage**](StoragesTaskApi.md#delete_storage) | **DELETE** /api/tasks/storages/{uuid} | Delete Api Storages


# **create_storage**
> List[Task] create_storage(storage_for_create=storage_for_create)

Post Api Storage

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.storage_for_create import StorageForCreate
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
    api_instance = virty_client.StoragesTaskApi(api_client)
    storage_for_create = virty_client.StorageForCreate() # StorageForCreate |  (optional)

    try:
        # Post Api Storage
        api_response = api_instance.create_storage(storage_for_create=storage_for_create)
        print("The response of StoragesTaskApi->create_storage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesTaskApi->create_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storage_for_create** | [**StorageForCreate**](StorageForCreate.md)|  | [optional] 

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

# **delete_storage**
> List[Task] delete_storage(uuid)

Delete Api Storages

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
    api_instance = virty_client.StoragesTaskApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Delete Api Storages
        api_response = api_instance.delete_storage(uuid)
        print("The response of StoragesTaskApi->delete_storage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesTaskApi->delete_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

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

