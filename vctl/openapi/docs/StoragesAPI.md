# \StoragesAPI

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateStoragePool**](StoragesAPI.md#CreateStoragePool) | **Post** /api/storages/pools | Post Api Storages Pools
[**GetStorage**](StoragesAPI.md#GetStorage) | **Get** /api/storages/{uuid} | Get Api Storages Uuid
[**GetStoragePools**](StoragesAPI.md#GetStoragePools) | **Get** /api/storages/pools | Get Api Storages Pools
[**GetStorages**](StoragesAPI.md#GetStorages) | **Get** /api/storages | Get Api Storages
[**UpdateStorageMetadata**](StoragesAPI.md#UpdateStorageMetadata) | **Patch** /api/storages | Post Api Storage
[**UpdateStoragePool**](StoragesAPI.md#UpdateStoragePool) | **Patch** /api/storages/pools | Post Api Storages Pools



## CreateStoragePool

> interface{} CreateStoragePool(ctx).StoragePoolForCreate(storagePoolForCreate).Execute()

Post Api Storages Pools

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
	storagePoolForCreate := *openapiclient.NewStoragePoolForCreate("Name_example", []string{"StorageUuids_example"}) // StoragePoolForCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StoragesAPI.CreateStoragePool(context.Background()).StoragePoolForCreate(storagePoolForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StoragesAPI.CreateStoragePool``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateStoragePool`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StoragesAPI.CreateStoragePool`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateStoragePoolRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storagePoolForCreate** | [**StoragePoolForCreate**](StoragePoolForCreate.md) |  | 

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


## GetStorage

> Storage GetStorage(ctx, uuid).Execute()

Get Api Storages Uuid

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
	uuid := "uuid_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StoragesAPI.GetStorage(context.Background(), uuid).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StoragesAPI.GetStorage``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStorage`: Storage
	fmt.Fprintf(os.Stdout, "Response from `StoragesAPI.GetStorage`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetStorageRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**Storage**](Storage.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetStoragePools

> []StoragePool GetStoragePools(ctx).Execute()

Get Api Storages Pools

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
	resp, r, err := apiClient.StoragesAPI.GetStoragePools(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StoragesAPI.GetStoragePools``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStoragePools`: []StoragePool
	fmt.Fprintf(os.Stdout, "Response from `StoragesAPI.GetStoragePools`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetStoragePoolsRequest struct via the builder pattern


### Return type

[**[]StoragePool**](StoragePool.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetStorages

> Storage GetStorages(ctx).Limit(limit).Page(page).Name(name).NodeName(nodeName).Execute()

Get Api Storages

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
	limit := int32(56) // int32 |  (optional) (default to 25)
	page := int32(56) // int32 |  (optional) (default to 0)
	name := "name_example" // string |  (optional)
	nodeName := "nodeName_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StoragesAPI.GetStorages(context.Background()).Limit(limit).Page(page).Name(name).NodeName(nodeName).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StoragesAPI.GetStorages``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStorages`: Storage
	fmt.Fprintf(os.Stdout, "Response from `StoragesAPI.GetStorages`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetStoragesRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 25]
 **page** | **int32** |  | [default to 0]
 **name** | **string** |  | 
 **nodeName** | **string** |  | 

### Return type

[**Storage**](Storage.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateStorageMetadata

> interface{} UpdateStorageMetadata(ctx).StorageMetadataForUpdate(storageMetadataForUpdate).Execute()

Post Api Storage

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
	storageMetadataForUpdate := *openapiclient.NewStorageMetadataForUpdate("Uuid_example", "Rool_example", "Protocol_example", "DeviceType_example") // StorageMetadataForUpdate |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StoragesAPI.UpdateStorageMetadata(context.Background()).StorageMetadataForUpdate(storageMetadataForUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StoragesAPI.UpdateStorageMetadata``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateStorageMetadata`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StoragesAPI.UpdateStorageMetadata`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUpdateStorageMetadataRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storageMetadataForUpdate** | [**StorageMetadataForUpdate**](StorageMetadataForUpdate.md) |  | 

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


## UpdateStoragePool

> interface{} UpdateStoragePool(ctx).StoragePoolForUpdate(storagePoolForUpdate).Execute()

Post Api Storages Pools

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
	storagePoolForUpdate := *openapiclient.NewStoragePoolForUpdate("Id_example", []string{"StorageUuids_example"}) // StoragePoolForUpdate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StoragesAPI.UpdateStoragePool(context.Background()).StoragePoolForUpdate(storagePoolForUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StoragesAPI.UpdateStoragePool``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateStoragePool`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StoragesAPI.UpdateStoragePool`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUpdateStoragePoolRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storagePoolForUpdate** | [**StoragePoolForUpdate**](StoragePoolForUpdate.md) |  | 

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

