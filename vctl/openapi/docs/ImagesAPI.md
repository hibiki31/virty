# \ImagesAPI

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetImages**](ImagesAPI.md#GetImages) | **Get** /api/images | Get Api Images
[**ScpImage**](ImagesAPI.md#ScpImage) | **Put** /api/images/scp | Put Api Images Scp
[**UpdateImageFlavor**](ImagesAPI.md#UpdateImageFlavor) | **Patch** /api/images | Patch Api Images



## GetImages

> Image GetImages(ctx).NodeName(nodeName).PoolUuid(poolUuid).Name(name).Rool(rool).Limit(limit).Page(page).Execute()

Get Api Images

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
	nodeName := "nodeName_example" // string |  (optional)
	poolUuid := "poolUuid_example" // string |  (optional)
	name := "name_example" // string |  (optional)
	rool := "rool_example" // string |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 25)
	page := int32(56) // int32 |  (optional) (default to 0)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ImagesAPI.GetImages(context.Background()).NodeName(nodeName).PoolUuid(poolUuid).Name(name).Rool(rool).Limit(limit).Page(page).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ImagesAPI.GetImages``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetImages`: Image
	fmt.Fprintf(os.Stdout, "Response from `ImagesAPI.GetImages`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetImagesRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **nodeName** | **string** |  | 
 **poolUuid** | **string** |  | 
 **name** | **string** |  | 
 **rool** | **string** |  | 
 **limit** | **int32** |  | [default to 25]
 **page** | **int32** |  | [default to 0]

### Return type

[**Image**](Image.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ScpImage

> interface{} ScpImage(ctx).ImageSCP(imageSCP).Execute()

Put Api Images Scp

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
	imageSCP := *openapiclient.NewImageSCP("FromNodeName_example", "ToNodeName_example", "FromFilePath_example", "ToFilePath_example") // ImageSCP |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ImagesAPI.ScpImage(context.Background()).ImageSCP(imageSCP).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ImagesAPI.ScpImage``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ScpImage`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ImagesAPI.ScpImage`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiScpImageRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **imageSCP** | [**ImageSCP**](ImageSCP.md) |  | 

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


## UpdateImageFlavor

> interface{} UpdateImageFlavor(ctx).ImageForUpdateImageFlavor(imageForUpdateImageFlavor).Execute()

Patch Api Images

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
	imageForUpdateImageFlavor := *openapiclient.NewImageForUpdateImageFlavor("StorageUuid_example", "Path_example", "NodeName_example", int32(123)) // ImageForUpdateImageFlavor | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ImagesAPI.UpdateImageFlavor(context.Background()).ImageForUpdateImageFlavor(imageForUpdateImageFlavor).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ImagesAPI.UpdateImageFlavor``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateImageFlavor`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ImagesAPI.UpdateImageFlavor`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUpdateImageFlavorRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **imageForUpdateImageFlavor** | [**ImageForUpdateImageFlavor**](ImageForUpdateImageFlavor.md) |  | 

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

