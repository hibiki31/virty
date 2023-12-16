# virty_client.MixinApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_version**](MixinApi.md#get_version) | **GET** /api/version | Get Version


# **get_version**
> Version get_version()

Get Version

初期化済みか判定用

### Example


```python
import time
import os
import virty_client
from virty_client.models.version import Version
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
    api_instance = virty_client.MixinApi(api_client)

    try:
        # Get Version
        api_response = api_instance.get_version()
        print("The response of MixinApi->get_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MixinApi->get_version: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**Version**](Version.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

