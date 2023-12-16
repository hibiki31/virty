# \FlavorsAPI

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateFlavor**](FlavorsAPI.md#CreateFlavor) | **Post** /api/flavors | Post Api Flavors
[**DeleteFlavor**](FlavorsAPI.md#DeleteFlavor) | **Delete** /api/flavors/{flavor_id} | Delete Flavors
[**GetFlavors**](FlavorsAPI.md#GetFlavors) | **Get** /api/flavors | Get Api Flavors



## CreateFlavor

> interface{} CreateFlavor(ctx).FlavorForCreate(flavorForCreate).Execute()

Post Api Flavors

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
	flavorForCreate := *openapiclient.NewFlavorForCreate("Name_example", "Os_example", "ManualUrl_example", "Icon_example", false, "Description_example") // FlavorForCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlavorsAPI.CreateFlavor(context.Background()).FlavorForCreate(flavorForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlavorsAPI.CreateFlavor``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateFlavor`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `FlavorsAPI.CreateFlavor`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateFlavorRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **flavorForCreate** | [**FlavorForCreate**](FlavorForCreate.md) |  | 

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


## DeleteFlavor

> FlavorPage DeleteFlavor(ctx, flavorId).Execute()

Delete Flavors

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
	flavorId := int32(56) // int32 | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlavorsAPI.DeleteFlavor(context.Background(), flavorId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlavorsAPI.DeleteFlavor``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteFlavor`: FlavorPage
	fmt.Fprintf(os.Stdout, "Response from `FlavorsAPI.DeleteFlavor`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**flavorId** | **int32** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteFlavorRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**FlavorPage**](FlavorPage.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetFlavors

> Flavor GetFlavors(ctx).Limit(limit).Page(page).Name(name).Execute()

Get Api Flavors

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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlavorsAPI.GetFlavors(context.Background()).Limit(limit).Page(page).Name(name).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlavorsAPI.GetFlavors``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetFlavors`: Flavor
	fmt.Fprintf(os.Stdout, "Response from `FlavorsAPI.GetFlavors`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetFlavorsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 25]
 **page** | **int32** |  | [default to 0]
 **name** | **string** |  | 

### Return type

[**Flavor**](Flavor.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

