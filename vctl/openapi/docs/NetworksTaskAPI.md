# \NetworksTaskAPI

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateNetwork**](NetworksTaskAPI.md#CreateNetwork) | **Post** /api/tasks/networks | Post Api Storage
[**CreateNetworkOvs**](NetworksTaskAPI.md#CreateNetworkOvs) | **Post** /api/tasks/networks/{uuid}/ovs | Post Uuid Ovs
[**DeleteNetwork**](NetworksTaskAPI.md#DeleteNetwork) | **Delete** /api/tasks/networks/{uuid} | Delete Api Storage
[**DeleteNetworkOvs**](NetworksTaskAPI.md#DeleteNetworkOvs) | **Delete** /api/tasks/networks/{uuid}/ovs/{name} | Post Api Networks Uuid Ovs
[**PostUuidOvsApiTasksNetworksProvidersPost**](NetworksTaskAPI.md#PostUuidOvsApiTasksNetworksProvidersPost) | **Post** /api/tasks/networks/providers | Post Uuid Ovs
[**RefreshNetworks**](NetworksTaskAPI.md#RefreshNetworks) | **Put** /api/tasks/networks | Put Api Networks



## CreateNetwork

> []Task CreateNetwork(ctx).NetworkForCreate(networkForCreate).Execute()

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
	networkForCreate := *openapiclient.NewNetworkForCreate("Name_example", "NodeName_example", "Type_example") // NetworkForCreate |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NetworksTaskAPI.CreateNetwork(context.Background()).NetworkForCreate(networkForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NetworksTaskAPI.CreateNetwork``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateNetwork`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NetworksTaskAPI.CreateNetwork`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateNetworkRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **networkForCreate** | [**NetworkForCreate**](NetworkForCreate.md) |  | 

### Return type

[**[]Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateNetworkOvs

> []Task CreateNetworkOvs(ctx, uuid).NetworkOVSForCreate(networkOVSForCreate).Execute()

Post Uuid Ovs

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
	networkOVSForCreate := *openapiclient.NewNetworkOVSForCreate(false, "Name_example") // NetworkOVSForCreate |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NetworksTaskAPI.CreateNetworkOvs(context.Background(), uuid).NetworkOVSForCreate(networkOVSForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NetworksTaskAPI.CreateNetworkOvs``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateNetworkOvs`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NetworksTaskAPI.CreateNetworkOvs`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCreateNetworkOvsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **networkOVSForCreate** | [**NetworkOVSForCreate**](NetworkOVSForCreate.md) |  | 

### Return type

[**[]Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteNetwork

> []Task DeleteNetwork(ctx, uuid).Execute()

Delete Api Storage

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
	resp, r, err := apiClient.NetworksTaskAPI.DeleteNetwork(context.Background(), uuid).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NetworksTaskAPI.DeleteNetwork``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteNetwork`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NetworksTaskAPI.DeleteNetwork`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteNetworkRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**[]Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteNetworkOvs

> []Task DeleteNetworkOvs(ctx, uuid, name).Execute()

Post Api Networks Uuid Ovs

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
	name := "name_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NetworksTaskAPI.DeleteNetworkOvs(context.Background(), uuid, name).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NetworksTaskAPI.DeleteNetworkOvs``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteNetworkOvs`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NetworksTaskAPI.DeleteNetworkOvs`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 
**name** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteNetworkOvsRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



### Return type

[**[]Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PostUuidOvsApiTasksNetworksProvidersPost

> []Task PostUuidOvsApiTasksNetworksProvidersPost(ctx).NetworkProviderForCreate(networkProviderForCreate).Execute()

Post Uuid Ovs

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
	networkProviderForCreate := *openapiclient.NewNetworkProviderForCreate() // NetworkProviderForCreate |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NetworksTaskAPI.PostUuidOvsApiTasksNetworksProvidersPost(context.Background()).NetworkProviderForCreate(networkProviderForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NetworksTaskAPI.PostUuidOvsApiTasksNetworksProvidersPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PostUuidOvsApiTasksNetworksProvidersPost`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NetworksTaskAPI.PostUuidOvsApiTasksNetworksProvidersPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPostUuidOvsApiTasksNetworksProvidersPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **networkProviderForCreate** | [**NetworkProviderForCreate**](NetworkProviderForCreate.md) |  | 

### Return type

[**[]Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RefreshNetworks

> []Task RefreshNetworks(ctx).Execute()

Put Api Networks

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
	resp, r, err := apiClient.NetworksTaskAPI.RefreshNetworks(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NetworksTaskAPI.RefreshNetworks``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RefreshNetworks`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NetworksTaskAPI.RefreshNetworks`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiRefreshNetworksRequest struct via the builder pattern


### Return type

[**[]Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

