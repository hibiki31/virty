# \ImagesTaskAPI

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DownloadImage**](ImagesTaskAPI.md#DownloadImage) | **Post** /api/tasks/images/download | Post Image Download
[**RefreshImages**](ImagesTaskAPI.md#RefreshImages) | **Put** /api/tasks/images | Put Api Images



## DownloadImage

> interface{} DownloadImage(ctx).ImageDownloadForCreate(imageDownloadForCreate).Execute()

Post Image Download

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	imageDownloadForCreate := *openapiclient.NewImageDownloadForCreate("StorageUuid_example", "ImageUrl_example") // ImageDownloadForCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ImagesTaskAPI.DownloadImage(context.Background()).ImageDownloadForCreate(imageDownloadForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ImagesTaskAPI.DownloadImage``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DownloadImage`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ImagesTaskAPI.DownloadImage`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDownloadImageRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **imageDownloadForCreate** | [**ImageDownloadForCreate**](ImageDownloadForCreate.md) |  | 

### Return type

**interface{}**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RefreshImages

> interface{} RefreshImages(ctx).Execute()

Put Api Images

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ImagesTaskAPI.RefreshImages(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ImagesTaskAPI.RefreshImages``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RefreshImages`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ImagesTaskAPI.RefreshImages`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiRefreshImagesRequest struct via the builder pattern


### Return type

**interface{}**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

