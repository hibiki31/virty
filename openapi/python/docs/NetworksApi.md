# virty_client.NetworksApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_network_pool**](NetworksApi.md#create_network_pool) | **POST** /api/networks/pools | Post Api Networks Pools
[**delete_network_pool**](NetworksApi.md#delete_network_pool) | **DELETE** /api/networks/pools/{id} | Delete Pools Uuid
[**get_network**](NetworksApi.md#get_network) | **GET** /api/networks/{uuid} | Get Api Networks Uuid
[**get_network_pools**](NetworksApi.md#get_network_pools) | **GET** /api/networks/pools | Get Api Networks Pools
[**get_networks**](NetworksApi.md#get_networks) | **GET** /api/networks | Get Api Networks
[**update_network_pool**](NetworksApi.md#update_network_pool) | **PATCH** /api/networks/pools | Patch Api Networks Pools


# **create_network_pool**
> object create_network_pool(network_pool_for_create)

Post Api Networks Pools

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_pool_for_create import NetworkPoolForCreate
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
    api_instance = virty_client.NetworksApi(api_client)
    network_pool_for_create = virty_client.NetworkPoolForCreate() # NetworkPoolForCreate | 

    try:
        # Post Api Networks Pools
        api_response = api_instance.create_network_pool(network_pool_for_create)
        print("The response of NetworksApi->create_network_pool:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksApi->create_network_pool: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **network_pool_for_create** | [**NetworkPoolForCreate**](NetworkPoolForCreate.md)|  | 

### Return type

**object**

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

# **delete_network_pool**
> object delete_network_pool(id)

Delete Pools Uuid

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
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
    api_instance = virty_client.NetworksApi(api_client)
    id = 56 # int | 

    try:
        # Delete Pools Uuid
        api_response = api_instance.delete_network_pool(id)
        print("The response of NetworksApi->delete_network_pool:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksApi->delete_network_pool: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

**object**

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

# **get_network**
> Network get_network(uuid)

Get Api Networks Uuid

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network import Network
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
    api_instance = virty_client.NetworksApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Api Networks Uuid
        api_response = api_instance.get_network(uuid)
        print("The response of NetworksApi->get_network:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksApi->get_network: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Network**](Network.md)

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

# **get_network_pools**
> List[NetworkPool] get_network_pools()

Get Api Networks Pools

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_pool import NetworkPool
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
    api_instance = virty_client.NetworksApi(api_client)

    try:
        # Get Api Networks Pools
        api_response = api_instance.get_network_pools()
        print("The response of NetworksApi->get_network_pools:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksApi->get_network_pools: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[NetworkPool]**](NetworkPool.md)

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

# **get_networks**
> NetworkPage get_networks(limit=limit, page=page, name_like=name_like, node_name_like=node_name_like, type=type)

Get Api Networks

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_page import NetworkPage
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
    api_instance = virty_client.NetworksApi(api_client)
    limit = 25 # int |  (optional) (default to 25)
    page = 0 # int |  (optional) (default to 0)
    name_like = 'name_like_example' # str |  (optional)
    node_name_like = 'node_name_like_example' # str |  (optional)
    type = 'type_example' # str |  (optional)

    try:
        # Get Api Networks
        api_response = api_instance.get_networks(limit=limit, page=page, name_like=name_like, node_name_like=node_name_like, type=type)
        print("The response of NetworksApi->get_networks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksApi->get_networks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 25]
 **page** | **int**|  | [optional] [default to 0]
 **name_like** | **str**|  | [optional] 
 **node_name_like** | **str**|  | [optional] 
 **type** | **str**|  | [optional] 

### Return type

[**NetworkPage**](NetworkPage.md)

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

# **update_network_pool**
> object update_network_pool(network_pool_for_update)

Patch Api Networks Pools

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_pool_for_update import NetworkPoolForUpdate
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
    api_instance = virty_client.NetworksApi(api_client)
    network_pool_for_update = virty_client.NetworkPoolForUpdate() # NetworkPoolForUpdate | 

    try:
        # Patch Api Networks Pools
        api_response = api_instance.update_network_pool(network_pool_for_update)
        print("The response of NetworksApi->update_network_pool:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NetworksApi->update_network_pool: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **network_pool_for_update** | [**NetworkPoolForUpdate**](NetworkPoolForUpdate.md)|  | 

### Return type

**object**

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

