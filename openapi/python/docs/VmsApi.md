# virty_client.VmsApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_vm**](VmsApi.md#get_vm) | **GET** /api/vms/{uuid} | Get Api Domain Uuid
[**get_vms**](VmsApi.md#get_vms) | **GET** /api/vms | Get Api Domain
[**get_vnc_address**](VmsApi.md#get_vnc_address) | **GET** /api/vms/vnc/{token} | Get Api Domain


# **get_vm**
> DomainDetail get_vm(uuid)

Get Api Domain Uuid

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.domain_detail import DomainDetail
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
    api_instance = virty_client.VmsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Api Domain Uuid
        api_response = api_instance.get_vm(uuid)
        print("The response of VmsApi->get_vm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsApi->get_vm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**DomainDetail**](DomainDetail.md)

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

# **get_vms**
> DomainPagenation get_vms(admin=admin, limit=limit, page=page, name_like=name_like, node_name_like=node_name_like)

Get Api Domain

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.domain_pagenation import DomainPagenation
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
    api_instance = virty_client.VmsApi(api_client)
    admin = False # bool |  (optional) (default to False)
    limit = 25 # int |  (optional) (default to 25)
    page = 0 # int |  (optional) (default to 0)
    name_like = 'name_like_example' # str |  (optional)
    node_name_like = 'node_name_like_example' # str |  (optional)

    try:
        # Get Api Domain
        api_response = api_instance.get_vms(admin=admin, limit=limit, page=page, name_like=name_like, node_name_like=node_name_like)
        print("The response of VmsApi->get_vms:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsApi->get_vms: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **admin** | **bool**|  | [optional] [default to False]
 **limit** | **int**|  | [optional] [default to 25]
 **page** | **int**|  | [optional] [default to 0]
 **name_like** | **str**|  | [optional] 
 **node_name_like** | **str**|  | [optional] 

### Return type

[**DomainPagenation**](DomainPagenation.md)

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

# **get_vnc_address**
> object get_vnc_address(token)

Get Api Domain

### Example


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


# Enter a context with an instance of the API client
with virty_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = virty_client.VmsApi(api_client)
    token = 'token_example' # str | 

    try:
        # Get Api Domain
        api_response = api_instance.get_vnc_address(token)
        print("The response of VmsApi->get_vnc_address:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsApi->get_vnc_address: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

