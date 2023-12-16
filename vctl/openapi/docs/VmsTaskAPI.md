# \VmsTaskAPI

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ControlVmCdrom**](VmsTaskAPI.md#ControlVmCdrom) | **Patch** /api/tasks/vms/{uuid}/cdrom | Patch Api Tasks Vms Uuid Cdrom
[**CreateVm**](VmsTaskAPI.md#CreateVm) | **Post** /api/tasks/vms | Post Api Vms
[**DeleteVm**](VmsTaskAPI.md#DeleteVm) | **Delete** /api/tasks/vms/{uuid} | Delete Api Domains
[**PathVmsProjectApiTasksVmsProjectPatch**](VmsTaskAPI.md#PathVmsProjectApiTasksVmsProjectPatch) | **Patch** /api/tasks/vms/project | Path Vms Project
[**RefreshVms**](VmsTaskAPI.md#RefreshVms) | **Put** /api/tasks/vms | Publish Task To Update Vm List
[**UpdateVmNetwork**](VmsTaskAPI.md#UpdateVmNetwork) | **Patch** /api/tasks/vms/{uuid}/network | Patch Api Vm Network
[**UpdateVmPowerStatus**](VmsTaskAPI.md#UpdateVmPowerStatus) | **Patch** /api/tasks/vms/{uuid}/power | Patch Api Tasks Vms Uuid Power



## ControlVmCdrom

> []Task ControlVmCdrom(ctx, uuid).CdromForUpdateDomain(cdromForUpdateDomain).Execute()

Patch Api Tasks Vms Uuid Cdrom



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
	cdromForUpdateDomain := *openapiclient.NewCdromForUpdateDomain() // CdromForUpdateDomain |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VmsTaskAPI.ControlVmCdrom(context.Background(), uuid).CdromForUpdateDomain(cdromForUpdateDomain).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VmsTaskAPI.ControlVmCdrom``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ControlVmCdrom`: []Task
	fmt.Fprintf(os.Stdout, "Response from `VmsTaskAPI.ControlVmCdrom`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiControlVmCdromRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **cdromForUpdateDomain** | [**CdromForUpdateDomain**](CdromForUpdateDomain.md) |  | 

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


## CreateVm

> []Task CreateVm(ctx).DomainForCreate(domainForCreate).Execute()

Post Api Vms

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
	domainForCreate := *openapiclient.NewDomainForCreate("Type_example", "Name_example", "NodeName_example", int32(123), int32(123), []openapiclient.DomainForCreateDisk{*openapiclient.NewDomainForCreateDisk("Type_example", "SavePoolUuid_example")}, []openapiclient.DomainForCreateInterface{*openapiclient.NewDomainForCreateInterface("Type_example", "NetworkUuid_example")}) // DomainForCreate |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VmsTaskAPI.CreateVm(context.Background()).DomainForCreate(domainForCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VmsTaskAPI.CreateVm``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateVm`: []Task
	fmt.Fprintf(os.Stdout, "Response from `VmsTaskAPI.CreateVm`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateVmRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **domainForCreate** | [**DomainForCreate**](DomainForCreate.md) |  | 

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


## DeleteVm

> []Task DeleteVm(ctx, uuid).Execute()

Delete Api Domains

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
	resp, r, err := apiClient.VmsTaskAPI.DeleteVm(context.Background(), uuid).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VmsTaskAPI.DeleteVm``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteVm`: []Task
	fmt.Fprintf(os.Stdout, "Response from `VmsTaskAPI.DeleteVm`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteVmRequest struct via the builder pattern


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


## PathVmsProjectApiTasksVmsProjectPatch

> interface{} PathVmsProjectApiTasksVmsProjectPatch(ctx).DomainProjectForUpdate(domainProjectForUpdate).Execute()

Path Vms Project

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
	domainProjectForUpdate := *openapiclient.NewDomainProjectForUpdate("Uuid_example", "ProjectId_example") // DomainProjectForUpdate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VmsTaskAPI.PathVmsProjectApiTasksVmsProjectPatch(context.Background()).DomainProjectForUpdate(domainProjectForUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VmsTaskAPI.PathVmsProjectApiTasksVmsProjectPatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PathVmsProjectApiTasksVmsProjectPatch`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `VmsTaskAPI.PathVmsProjectApiTasksVmsProjectPatch`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPathVmsProjectApiTasksVmsProjectPatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **domainProjectForUpdate** | [**DomainProjectForUpdate**](DomainProjectForUpdate.md) |  | 

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


## RefreshVms

> []Task RefreshVms(ctx).Execute()

Publish Task To Update Vm List

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
	resp, r, err := apiClient.VmsTaskAPI.RefreshVms(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VmsTaskAPI.RefreshVms``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RefreshVms`: []Task
	fmt.Fprintf(os.Stdout, "Response from `VmsTaskAPI.RefreshVms`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiRefreshVmsRequest struct via the builder pattern


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


## UpdateVmNetwork

> []Task UpdateVmNetwork(ctx, uuid).NetworkForUpdateDomain(networkForUpdateDomain).Execute()

Patch Api Vm Network



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
	networkForUpdateDomain := *openapiclient.NewNetworkForUpdateDomain("Mac_example", "NetworkUuid_example") // NetworkForUpdateDomain |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VmsTaskAPI.UpdateVmNetwork(context.Background(), uuid).NetworkForUpdateDomain(networkForUpdateDomain).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VmsTaskAPI.UpdateVmNetwork``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateVmNetwork`: []Task
	fmt.Fprintf(os.Stdout, "Response from `VmsTaskAPI.UpdateVmNetwork`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateVmNetworkRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **networkForUpdateDomain** | [**NetworkForUpdateDomain**](NetworkForUpdateDomain.md) |  | 

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


## UpdateVmPowerStatus

> []Task UpdateVmPowerStatus(ctx, uuid).PowerStatusForUpdateDomain(powerStatusForUpdateDomain).Execute()

Patch Api Tasks Vms Uuid Power

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
	powerStatusForUpdateDomain := *openapiclient.NewPowerStatusForUpdateDomain() // PowerStatusForUpdateDomain |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VmsTaskAPI.UpdateVmPowerStatus(context.Background(), uuid).PowerStatusForUpdateDomain(powerStatusForUpdateDomain).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VmsTaskAPI.UpdateVmPowerStatus``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateVmPowerStatus`: []Task
	fmt.Fprintf(os.Stdout, "Response from `VmsTaskAPI.UpdateVmPowerStatus`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**uuid** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateVmPowerStatusRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **powerStatusForUpdateDomain** | [**PowerStatusForUpdateDomain**](PowerStatusForUpdateDomain.md) |  | 

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

