# virty_client.NetworksTaskApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_network**](NetworksTaskApi.md#create_network) | **POST** /api/tasks/networks | Post Api Storage
[**create_network_ovs**](NetworksTaskApi.md#create_network_ovs) | **POST** /api/tasks/networks/{uuid}/ovs | Post Uuid Ovs
[**delete_network**](NetworksTaskApi.md#delete_network) | **DELETE** /api/tasks/networks/{uuid} | Delete Api Storage
[**delete_network_ovs**](NetworksTaskApi.md#delete_network_ovs) | **DELETE** /api/tasks/networks/{uuid}/ovs/{name} | Post Api Networks Uuid Ovs
[**post_uuid_ovs_api_tasks_networks_providers_post**](NetworksTaskApi.md#post_uuid_ovs_api_tasks_networks_providers_post) | **POST** /api/tasks/networks/providers | Post Uuid Ovs
[**refresh_networks**](NetworksTaskApi.md#refresh_networks) | **PUT** /api/tasks/networks | Put Api Networks


# **create_network**
> List[Task] create_network(network_for_create=network_for_create)

Post Api Storage

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_for_create import NetworkForCreate
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
    api_instance = virty_client.NetworksTaskApi(api_client)
    network_for_create = virty_client.NetworkForCreate() # NetworkForCreate |  (optional)

    try:
        # Post Api Storage
        api_response = api_instance.create_network(network_for_create=network_for_create)
        print("The response of NetworksTaskApi->create_network:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksTaskApi->create_network: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **network_for_create** | [**NetworkForCreate**](NetworkForCreate.md)|  | [optional] 

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

# **create_network_ovs**
> List[Task] create_network_ovs(uuid, network_ovs_for_create=network_ovs_for_create)

Post Uuid Ovs

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_ovs_for_create import NetworkOVSForCreate
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
    api_instance = virty_client.NetworksTaskApi(api_client)
    uuid = 'uuid_example' # str | 
    network_ovs_for_create = virty_client.NetworkOVSForCreate() # NetworkOVSForCreate |  (optional)

    try:
        # Post Uuid Ovs
        api_response = api_instance.create_network_ovs(uuid, network_ovs_for_create=network_ovs_for_create)
        print("The response of NetworksTaskApi->create_network_ovs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksTaskApi->create_network_ovs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **network_ovs_for_create** | [**NetworkOVSForCreate**](NetworkOVSForCreate.md)|  | [optional] 

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

# **delete_network**
> List[Task] delete_network(uuid)

Delete Api Storage

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
    api_instance = virty_client.NetworksTaskApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Delete Api Storage
        api_response = api_instance.delete_network(uuid)
        print("The response of NetworksTaskApi->delete_network:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksTaskApi->delete_network: %s\n" % e)
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

# **delete_network_ovs**
> List[Task] delete_network_ovs(uuid, name)

Post Api Networks Uuid Ovs

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
    api_instance = virty_client.NetworksTaskApi(api_client)
    uuid = 'uuid_example' # str | 
    name = 'name_example' # str | 

    try:
        # Post Api Networks Uuid Ovs
        api_response = api_instance.delete_network_ovs(uuid, name)
        print("The response of NetworksTaskApi->delete_network_ovs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksTaskApi->delete_network_ovs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
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

# **post_uuid_ovs_api_tasks_networks_providers_post**
> List[Task] post_uuid_ovs_api_tasks_networks_providers_post(network_provider_for_create=network_provider_for_create)

Post Uuid Ovs

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_provider_for_create import NetworkProviderForCreate
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
    api_instance = virty_client.NetworksTaskApi(api_client)
    network_provider_for_create = virty_client.NetworkProviderForCreate() # NetworkProviderForCreate |  (optional)

    try:
        # Post Uuid Ovs
        api_response = api_instance.post_uuid_ovs_api_tasks_networks_providers_post(network_provider_for_create=network_provider_for_create)
        print("The response of NetworksTaskApi->post_uuid_ovs_api_tasks_networks_providers_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksTaskApi->post_uuid_ovs_api_tasks_networks_providers_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **network_provider_for_create** | [**NetworkProviderForCreate**](NetworkProviderForCreate.md)|  | [optional] 

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

# **refresh_networks**
> List[Task] refresh_networks()

Put Api Networks

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
    api_instance = virty_client.NetworksTaskApi(api_client)

    try:
        # Put Api Networks
        api_response = api_instance.refresh_networks()
        print("The response of NetworksTaskApi->refresh_networks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksTaskApi->refresh_networks: %s\n" % e)
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

