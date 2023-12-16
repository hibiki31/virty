# virty_client.TasksApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_tasks**](TasksApi.md#delete_tasks) | **DELETE** /api/tasks/ | Delete Tasks
[**get_incomplete_tasks**](TasksApi.md#get_incomplete_tasks) | **GET** /api/tasks/incomplete | Get Tasks Incomplete
[**get_task**](TasksApi.md#get_task) | **GET** /api/tasks/{uuid} | Get Tasks
[**get_tasks**](TasksApi.md#get_tasks) | **GET** /api/tasks | Get Tasks


# **delete_tasks**
> List[Task] delete_tasks()

Delete Tasks

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
    api_instance = virty_client.TasksApi(api_client)

    try:
        # Delete Tasks
        api_response = api_instance.delete_tasks()
        print("The response of TasksApi->delete_tasks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->delete_tasks: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_incomplete_tasks**
> TaskIncomplete get_incomplete_tasks(hash=hash, admin=admin)

Get Tasks Incomplete

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.task_incomplete import TaskIncomplete
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
    api_instance = virty_client.TasksApi(api_client)
    hash = 'hash_example' # str |  (optional)
    admin = False # bool |  (optional) (default to False)

    try:
        # Get Tasks Incomplete
        api_response = api_instance.get_incomplete_tasks(hash=hash, admin=admin)
        print("The response of TasksApi->get_incomplete_tasks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->get_incomplete_tasks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hash** | **str**|  | [optional] 
 **admin** | **bool**|  | [optional] [default to False]

### Return type

[**TaskIncomplete**](TaskIncomplete.md)

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

# **get_task**
> Task get_task(uuid)

Get Tasks

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
    api_instance = virty_client.TasksApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Tasks
        api_response = api_instance.get_task(uuid)
        print("The response of TasksApi->get_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->get_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Task**](Task.md)

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

# **get_tasks**
> TaskPagesnation get_tasks(admin=admin, limit=limit, page=page, resource=resource, object=object, method=method, status=status)

Get Tasks

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.task_pagesnation import TaskPagesnation
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
    api_instance = virty_client.TasksApi(api_client)
    admin = False # bool |  (optional) (default to False)
    limit = 25 # int |  (optional) (default to 25)
    page = 0 # int |  (optional) (default to 0)
    resource = 'resource_example' # str |  (optional)
    object = 'object_example' # str |  (optional)
    method = 'method_example' # str |  (optional)
    status = 'status_example' # str |  (optional)

    try:
        # Get Tasks
        api_response = api_instance.get_tasks(admin=admin, limit=limit, page=page, resource=resource, object=object, method=method, status=status)
        print("The response of TasksApi->get_tasks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksApi->get_tasks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **admin** | **bool**|  | [optional] [default to False]
 **limit** | **int**|  | [optional] [default to 25]
 **page** | **int**|  | [optional] [default to 0]
 **resource** | **str**|  | [optional] 
 **object** | **str**|  | [optional] 
 **method** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 

### Return type

[**TaskPagesnation**](TaskPagesnation.md)

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

