# virty_client.ImagesTaskApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**download_image**](ImagesTaskApi.md#download_image) | **POST** /api/tasks/images/download | Post Image Download
[**refresh_images**](ImagesTaskApi.md#refresh_images) | **PUT** /api/tasks/images | Put Api Images


# **download_image**
> object download_image(image_download_for_create)

Post Image Download

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.image_download_for_create import ImageDownloadForCreate
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
    api_instance = virty_client.ImagesTaskApi(api_client)
    image_download_for_create = virty_client.ImageDownloadForCreate() # ImageDownloadForCreate | 

    try:
        # Post Image Download
        api_response = api_instance.download_image(image_download_for_create)
        print("The response of ImagesTaskApi->download_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImagesTaskApi->download_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_download_for_create** | [**ImageDownloadForCreate**](ImageDownloadForCreate.md)|  | 

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

# **refresh_images**
> object refresh_images()

Put Api Images

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
    api_instance = virty_client.ImagesTaskApi(api_client)

    try:
        # Put Api Images
        api_response = api_instance.refresh_images()
        print("The response of ImagesTaskApi->refresh_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImagesTaskApi->refresh_images: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

