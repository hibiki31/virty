# virty_client.MetricsApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_metrics**](MetricsApi.md#get_metrics) | **GET** /api/metrics | Exporter Get


# **get_metrics**
> str get_metrics()

Exporter Get

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
    api_instance = virty_client.MetricsApi(api_client)

    try:
        # Exporter Get
        api_response = api_instance.get_metrics()
        print("The response of MetricsApi->get_metrics:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetricsApi->get_metrics: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

