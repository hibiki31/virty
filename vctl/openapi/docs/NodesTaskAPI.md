# \NodesTaskAPI

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateNode**](NodesTaskAPI.md#CreateNode) | **Post** /api/tasks/nodes | Post Tasks Nodes
[**DeleteNode**](NodesTaskAPI.md#DeleteNode) | **Delete** /api/tasks/nodes/{name} | Delete Tasks Nodes Name
[**UpdateNodeRole**](NodesTaskAPI.md#UpdateNodeRole) | **Patch** /api/tasks/nodes/roles | Patch Api Node Role



## CreateNode

> []Task CreateNode(ctx).NodeForCreate(nodeForCreate).Execute()

Post Tasks Nodes

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
	nodeForCreate := *openapiclient.NewNodeForCreate("Name_example", "Description_example", "Domain_example", "UserName_example", int32(123), false) // NodeForCreate |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NodesTaskAPI.CreateNode(context.Background()).NodeForCreate(nodeForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NodesTaskAPI.CreateNode``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateNode`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NodesTaskAPI.CreateNode`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateNodeRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **nodeForCreate** | [**NodeForCreate**](NodeForCreate.md) |  | 

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


## DeleteNode

> []Task DeleteNode(ctx, name).Execute()

Delete Tasks Nodes Name

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
	name := "name_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NodesTaskAPI.DeleteNode(context.Background(), name).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NodesTaskAPI.DeleteNode``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteNode`: []Task
	fmt.Fprintf(os.Stdout, "Response from `NodesTaskAPI.DeleteNode`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**name** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteNodeRequest struct via the builder pattern


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


## UpdateNodeRole

> Task UpdateNodeRole(ctx).NodeRoleForUpdate(nodeRoleForUpdate).Execute()

Patch Api Node Role

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
	nodeRoleForUpdate := *openapiclient.NewNodeRoleForUpdate("NodeName_example", "RoleName_example") // NodeRoleForUpdate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NodesTaskAPI.UpdateNodeRole(context.Background()).NodeRoleForUpdate(nodeRoleForUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NodesTaskAPI.UpdateNodeRole``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateNodeRole`: Task
	fmt.Fprintf(os.Stdout, "Response from `NodesTaskAPI.UpdateNodeRole`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUpdateNodeRoleRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **nodeRoleForUpdate** | [**NodeRoleForUpdate**](NodeRoleForUpdate.md) |  | 

### Return type

[**Task**](Task.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

