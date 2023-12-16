# virty_client.ImagesApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_images**](ImagesApi.md#get_images) | **GET** /api/images | Get Api Images
[**scp_image**](ImagesApi.md#scp_image) | **PUT** /api/images/scp | Put Api Images Scp
[**update_image_flavor**](ImagesApi.md#update_image_flavor) | **PATCH** /api/images | Patch Api Images


# **get_images**
> Image get_images(node_name=node_name, pool_uuid=pool_uuid, name=name, rool=rool, limit=limit, page=page)

Get Api Images

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.image import Image
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
    api_instance = virty_client.ImagesApi(api_client)
    node_name = 'node_name_example' # str |  (optional)
    pool_uuid = 'pool_uuid_example' # str |  (optional)
    name = 'name_example' # str |  (optional)
    rool = 'rool_example' # str |  (optional)
    limit = 25 # int |  (optional) (default to 25)
    page = 0 # int |  (optional) (default to 0)

    try:
        # Get Api Images
        api_response = api_instance.get_images(node_name=node_name, pool_uuid=pool_uuid, name=name, rool=rool, limit=limit, page=page)
        print("The response of ImagesApi->get_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImagesApi->get_images: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_name** | **str**|  | [optional] 
 **pool_uuid** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **rool** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 25]
 **page** | **int**|  | [optional] [default to 0]

### Return type

[**Image**](Image.md)

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

# **scp_image**
> object scp_image(image_scp=image_scp)

Put Api Images Scp

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.image_scp import ImageSCP
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
    api_instance = virty_client.ImagesApi(api_client)
    image_scp = virty_client.ImageSCP() # ImageSCP |  (optional)

    try:
        # Put Api Images Scp
        api_response = api_instance.scp_image(image_scp=image_scp)
        print("The response of ImagesApi->scp_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImagesApi->scp_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_scp** | [**ImageSCP**](ImageSCP.md)|  | [optional] 

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

# **update_image_flavor**
> object update_image_flavor(image_for_update_image_flavor)

Patch Api Images

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.image_for_update_image_flavor import ImageForUpdateImageFlavor
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
    api_instance = virty_client.ImagesApi(api_client)
    image_for_update_image_flavor = virty_client.ImageForUpdateImageFlavor() # ImageForUpdateImageFlavor | 

    try:
        # Patch Api Images
        api_response = api_instance.update_image_flavor(image_for_update_image_flavor)
        print("The response of ImagesApi->update_image_flavor:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImagesApi->update_image_flavor: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_for_update_image_flavor** | [**ImageForUpdateImageFlavor**](ImageForUpdateImageFlavor.md)|  | 

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

