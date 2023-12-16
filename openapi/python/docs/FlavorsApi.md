# virty_client.FlavorsApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_flavor**](FlavorsApi.md#create_flavor) | **POST** /api/flavors | Post Api Flavors
[**delete_flavor**](FlavorsApi.md#delete_flavor) | **DELETE** /api/flavors/{flavor_id} | Delete Flavors
[**get_flavors**](FlavorsApi.md#get_flavors) | **GET** /api/flavors | Get Api Flavors


# **create_flavor**
> object create_flavor(flavor_for_create)

Post Api Flavors

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.flavor_for_create import FlavorForCreate
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
    api_instance = virty_client.FlavorsApi(api_client)
    flavor_for_create = virty_client.FlavorForCreate() # FlavorForCreate | 

    try:
        # Post Api Flavors
        api_response = api_instance.create_flavor(flavor_for_create)
        print("The response of FlavorsApi->create_flavor:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlavorsApi->create_flavor: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **flavor_for_create** | [**FlavorForCreate**](FlavorForCreate.md)|  | 

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

# **delete_flavor**
> FlavorPage delete_flavor(flavor_id)

Delete Flavors

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.flavor_page import FlavorPage
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
    api_instance = virty_client.FlavorsApi(api_client)
    flavor_id = 56 # int | 

    try:
        # Delete Flavors
        api_response = api_instance.delete_flavor(flavor_id)
        print("The response of FlavorsApi->delete_flavor:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlavorsApi->delete_flavor: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **flavor_id** | **int**|  | 

### Return type

[**FlavorPage**](FlavorPage.md)

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

# **get_flavors**
> Flavor get_flavors(limit=limit, page=page, name=name)

Get Api Flavors

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.flavor import Flavor
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
    api_instance = virty_client.FlavorsApi(api_client)
    limit = 25 # int |  (optional) (default to 25)
    page = 0 # int |  (optional) (default to 0)
    name = 'name_example' # str |  (optional)

    try:
        # Get Api Flavors
        api_response = api_instance.get_flavors(limit=limit, page=page, name=name)
        print("The response of FlavorsApi->get_flavors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlavorsApi->get_flavors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 25]
 **page** | **int**|  | [optional] [default to 0]
 **name** | **str**|  | [optional] 

### Return type

[**Flavor**](Flavor.md)

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

