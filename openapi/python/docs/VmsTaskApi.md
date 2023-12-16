# virty_client.VmsTaskApi

All URIs are relative to *https://virty-pr.hinagiku.me/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**control_vm_cdrom**](VmsTaskApi.md#control_vm_cdrom) | **PATCH** /api/tasks/vms/{uuid}/cdrom | Patch Api Tasks Vms Uuid Cdrom
[**create_vm**](VmsTaskApi.md#create_vm) | **POST** /api/tasks/vms | Post Api Vms
[**delete_vm**](VmsTaskApi.md#delete_vm) | **DELETE** /api/tasks/vms/{uuid} | Delete Api Domains
[**path_vms_project_api_tasks_vms_project_patch**](VmsTaskApi.md#path_vms_project_api_tasks_vms_project_patch) | **PATCH** /api/tasks/vms/project | Path Vms Project
[**refresh_vms**](VmsTaskApi.md#refresh_vms) | **PUT** /api/tasks/vms | Publish Task To Update Vm List
[**update_vm_network**](VmsTaskApi.md#update_vm_network) | **PATCH** /api/tasks/vms/{uuid}/network | Patch Api Vm Network
[**update_vm_power_status**](VmsTaskApi.md#update_vm_power_status) | **PATCH** /api/tasks/vms/{uuid}/power | Patch Api Tasks Vms Uuid Power


# **control_vm_cdrom**
> List[Task] control_vm_cdrom(uuid, cdrom_for_update_domain=cdrom_for_update_domain)

Patch Api Tasks Vms Uuid Cdrom

umount - path = null  mount - path = iso file path

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.cdrom_for_update_domain import CdromForUpdateDomain
from virty_client.models.task import Task
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
    api_instance = virty_client.VmsTaskApi(api_client)
    uuid = 'uuid_example' # str | 
    cdrom_for_update_domain = virty_client.CdromForUpdateDomain() # CdromForUpdateDomain |  (optional)

    try:
        # Patch Api Tasks Vms Uuid Cdrom
        api_response = api_instance.control_vm_cdrom(uuid, cdrom_for_update_domain=cdrom_for_update_domain)
        print("The response of VmsTaskApi->control_vm_cdrom:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsTaskApi->control_vm_cdrom: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **cdrom_for_update_domain** | [**CdromForUpdateDomain**](CdromForUpdateDomain.md)|  | [optional] 

### Return type

[**List[Task]**](Task.md)

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

# **create_vm**
> List[Task] create_vm(domain_for_create=domain_for_create)

Post Api Vms

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.domain_for_create import DomainForCreate
from virty_client.models.task import Task
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
    api_instance = virty_client.VmsTaskApi(api_client)
    domain_for_create = virty_client.DomainForCreate() # DomainForCreate |  (optional)

    try:
        # Post Api Vms
        api_response = api_instance.create_vm(domain_for_create=domain_for_create)
        print("The response of VmsTaskApi->create_vm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsTaskApi->create_vm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **domain_for_create** | [**DomainForCreate**](DomainForCreate.md)|  | [optional] 

### Return type

[**List[Task]**](Task.md)

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

# **delete_vm**
> List[Task] delete_vm(uuid)

Delete Api Domains

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.task import Task
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
    api_instance = virty_client.VmsTaskApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Delete Api Domains
        api_response = api_instance.delete_vm(uuid)
        print("The response of VmsTaskApi->delete_vm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsTaskApi->delete_vm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**List[Task]**](Task.md)

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

# **path_vms_project_api_tasks_vms_project_patch**
> object path_vms_project_api_tasks_vms_project_patch(domain_project_for_update)

Path Vms Project

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.domain_project_for_update import DomainProjectForUpdate
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
    api_instance = virty_client.VmsTaskApi(api_client)
    domain_project_for_update = virty_client.DomainProjectForUpdate() # DomainProjectForUpdate | 

    try:
        # Path Vms Project
        api_response = api_instance.path_vms_project_api_tasks_vms_project_patch(domain_project_for_update)
        print("The response of VmsTaskApi->path_vms_project_api_tasks_vms_project_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsTaskApi->path_vms_project_api_tasks_vms_project_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **domain_project_for_update** | [**DomainProjectForUpdate**](DomainProjectForUpdate.md)|  | 

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

# **refresh_vms**
> List[Task] refresh_vms()

Publish Task To Update Vm List

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.task import Task
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
    api_instance = virty_client.VmsTaskApi(api_client)

    try:
        # Publish Task To Update Vm List
        api_response = api_instance.refresh_vms()
        print("The response of VmsTaskApi->refresh_vms:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsTaskApi->refresh_vms: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[Task]**](Task.md)

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

# **update_vm_network**
> List[Task] update_vm_network(uuid, network_for_update_domain=network_for_update_domain)

Patch Api Vm Network

**Power off required**  Exception: Cannot switch the OVS while the VM is runningOperation not supported: unable to change config on 'network' network type

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.network_for_update_domain import NetworkForUpdateDomain
from virty_client.models.task import Task
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
    api_instance = virty_client.VmsTaskApi(api_client)
    uuid = 'uuid_example' # str | 
    network_for_update_domain = virty_client.NetworkForUpdateDomain() # NetworkForUpdateDomain |  (optional)

    try:
        # Patch Api Vm Network
        api_response = api_instance.update_vm_network(uuid, network_for_update_domain=network_for_update_domain)
        print("The response of VmsTaskApi->update_vm_network:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsTaskApi->update_vm_network: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **network_for_update_domain** | [**NetworkForUpdateDomain**](NetworkForUpdateDomain.md)|  | [optional] 

### Return type

[**List[Task]**](Task.md)

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

# **update_vm_power_status**
> List[Task] update_vm_power_status(uuid, power_status_for_update_domain=power_status_for_update_domain)

Patch Api Tasks Vms Uuid Power

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import time
import os
import virty_client
from virty_client.models.power_status_for_update_domain import PowerStatusForUpdateDomain
from virty_client.models.task import Task
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
    api_instance = virty_client.VmsTaskApi(api_client)
    uuid = 'uuid_example' # str | 
    power_status_for_update_domain = virty_client.PowerStatusForUpdateDomain() # PowerStatusForUpdateDomain |  (optional)

    try:
        # Patch Api Tasks Vms Uuid Power
        api_response = api_instance.update_vm_power_status(uuid, power_status_for_update_domain=power_status_for_update_domain)
        print("The response of VmsTaskApi->update_vm_power_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VmsTaskApi->update_vm_power_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **power_status_for_update_domain** | [**PowerStatusForUpdateDomain**](PowerStatusForUpdateDomain.md)|  | [optional] 

### Return type

[**List[Task]**](Task.md)

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

