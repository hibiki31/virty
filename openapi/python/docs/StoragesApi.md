# virty_client.StoragesApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_storage_pool**](StoragesApi.md#create_storage_pool) | **POST** /api/storages/pools | Post Api Storages Pools
[**get_storage**](StoragesApi.md#get_storage) | **GET** /api/storages/{uuid} | Get Api Storages Uuid
[**get_storage_pools**](StoragesApi.md#get_storage_pools) | **GET** /api/storages/pools | Get Api Storages Pools
[**get_storages**](StoragesApi.md#get_storages) | **GET** /api/storages | Get Api Storages
[**update_storage_metadata**](StoragesApi.md#update_storage_metadata) | **PATCH** /api/storages | Post Api Storage
[**update_storage_pool**](StoragesApi.md#update_storage_pool) | **PATCH** /api/storages/pools | Post Api Storages Pools


# **create_storage_pool**
> object create_storage_pool(storage_pool_for_create)

Post Api Storages Pools

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.storage_pool_for_create import StoragePoolForCreate
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
    api_instance = virty_client.StoragesApi(api_client)
    storage_pool_for_create = virty_client.StoragePoolForCreate() # StoragePoolForCreate | 

    try:
        # Post Api Storages Pools
        api_response = api_instance.create_storage_pool(storage_pool_for_create)
        print("The response of StoragesApi->create_storage_pool:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesApi->create_storage_pool: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storage_pool_for_create** | [**StoragePoolForCreate**](StoragePoolForCreate.md)|  | 

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

# **get_storage**
> Storage get_storage(uuid)

Get Api Storages Uuid

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.storage import Storage
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
    api_instance = virty_client.StoragesApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Api Storages Uuid
        api_response = api_instance.get_storage(uuid)
        print("The response of StoragesApi->get_storage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesApi->get_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Storage**](Storage.md)

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

# **get_storage_pools**
> List[StoragePool] get_storage_pools()

Get Api Storages Pools

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.storage_pool import StoragePool
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
    api_instance = virty_client.StoragesApi(api_client)

    try:
        # Get Api Storages Pools
        api_response = api_instance.get_storage_pools()
        print("The response of StoragesApi->get_storage_pools:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesApi->get_storage_pools: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[StoragePool]**](StoragePool.md)

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

# **get_storages**
> Storage get_storages(limit=limit, page=page, name=name, node_name=node_name)

Get Api Storages

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.storage import Storage
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
    api_instance = virty_client.StoragesApi(api_client)
    limit = 25 # int |  (optional) (default to 25)
    page = 0 # int |  (optional) (default to 0)
    name = 'name_example' # str |  (optional)
    node_name = 'node_name_example' # str |  (optional)

    try:
        # Get Api Storages
        api_response = api_instance.get_storages(limit=limit, page=page, name=name, node_name=node_name)
        print("The response of StoragesApi->get_storages:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesApi->get_storages: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 25]
 **page** | **int**|  | [optional] [default to 0]
 **name** | **str**|  | [optional] 
 **node_name** | **str**|  | [optional] 

### Return type

[**Storage**](Storage.md)

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

# **update_storage_metadata**
> object update_storage_metadata(storage_metadata_for_update=storage_metadata_for_update)

Post Api Storage

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.storage_metadata_for_update import StorageMetadataForUpdate
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
    api_instance = virty_client.StoragesApi(api_client)
    storage_metadata_for_update = virty_client.StorageMetadataForUpdate() # StorageMetadataForUpdate |  (optional)

    try:
        # Post Api Storage
        api_response = api_instance.update_storage_metadata(storage_metadata_for_update=storage_metadata_for_update)
        print("The response of StoragesApi->update_storage_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesApi->update_storage_metadata: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storage_metadata_for_update** | [**StorageMetadataForUpdate**](StorageMetadataForUpdate.md)|  | [optional] 

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

# **update_storage_pool**
> object update_storage_pool(storage_pool_for_update)

Post Api Storages Pools

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.storage_pool_for_update import StoragePoolForUpdate
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
    api_instance = virty_client.StoragesApi(api_client)
    storage_pool_for_update = virty_client.StoragePoolForUpdate() # StoragePoolForUpdate | 

    try:
        # Post Api Storages Pools
        api_response = api_instance.update_storage_pool(storage_pool_for_update)
        print("The response of StoragesApi->update_storage_pool:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StoragesApi->update_storage_pool: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storage_pool_for_update** | [**StoragePoolForUpdate**](StoragePoolForUpdate.md)|  | 

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

