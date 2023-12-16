# NodePage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**Description** | **string** |  | 
**Domain** | **string** |  | 
**UserName** | **string** |  | 
**Port** | **int32** |  | 
**Core** | **int32** |  | 
**Memory** | **int32** |  | 
**CpuGen** | **string** |  | 
**OsLike** | **string** |  | 
**OsName** | **string** |  | 
**OsVersion** | **string** |  | 
**Status** | **int32** |  | 
**QemuVersion** | Pointer to **string** |  | [optional] 
**LibvirtVersion** | Pointer to **string** |  | [optional] 
**Roles** | [**[]NodeRole**](NodeRole.md) |  | 

## Methods

### NewNodePage

`func NewNodePage(name string, description string, domain string, userName string, port int32, core int32, memory int32, cpuGen string, osLike string, osName string, osVersion string, status int32, roles []NodeRole, ) *NodePage`

NewNodePage instantiates a new NodePage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNodePageWithDefaults

`func NewNodePageWithDefaults() *NodePage`

NewNodePageWithDefaults instantiates a new NodePage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *NodePage) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *NodePage) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *NodePage) SetName(v string)`

SetName sets Name field to given value.


### GetDescription

`func (o *NodePage) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *NodePage) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *NodePage) SetDescription(v string)`

SetDescription sets Description field to given value.


### GetDomain

`func (o *NodePage) GetDomain() string`

GetDomain returns the Domain field if non-nil, zero value otherwise.

### GetDomainOk

`func (o *NodePage) GetDomainOk() (*string, bool)`

GetDomainOk returns a tuple with the Domain field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDomain

`func (o *NodePage) SetDomain(v string)`

SetDomain sets Domain field to given value.


### GetUserName

`func (o *NodePage) GetUserName() string`

GetUserName returns the UserName field if non-nil, zero value otherwise.

### GetUserNameOk

`func (o *NodePage) GetUserNameOk() (*string, bool)`

GetUserNameOk returns a tuple with the UserName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserName

`func (o *NodePage) SetUserName(v string)`

SetUserName sets UserName field to given value.


### GetPort

`func (o *NodePage) GetPort() int32`

GetPort returns the Port field if non-nil, zero value otherwise.

### GetPortOk

`func (o *NodePage) GetPortOk() (*int32, bool)`

GetPortOk returns a tuple with the Port field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPort

`func (o *NodePage) SetPort(v int32)`

SetPort sets Port field to given value.


### GetCore

`func (o *NodePage) GetCore() int32`

GetCore returns the Core field if non-nil, zero value otherwise.

### GetCoreOk

`func (o *NodePage) GetCoreOk() (*int32, bool)`

GetCoreOk returns a tuple with the Core field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCore

`func (o *NodePage) SetCore(v int32)`

SetCore sets Core field to given value.


### GetMemory

`func (o *NodePage) GetMemory() int32`

GetMemory returns the Memory field if non-nil, zero value otherwise.

### GetMemoryOk

`func (o *NodePage) GetMemoryOk() (*int32, bool)`

GetMemoryOk returns a tuple with the Memory field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemory

`func (o *NodePage) SetMemory(v int32)`

SetMemory sets Memory field to given value.


### GetCpuGen

`func (o *NodePage) GetCpuGen() string`

GetCpuGen returns the CpuGen field if non-nil, zero value otherwise.

### GetCpuGenOk

`func (o *NodePage) GetCpuGenOk() (*string, bool)`

GetCpuGenOk returns a tuple with the CpuGen field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCpuGen

`func (o *NodePage) SetCpuGen(v string)`

SetCpuGen sets CpuGen field to given value.


### GetOsLike

`func (o *NodePage) GetOsLike() string`

GetOsLike returns the OsLike field if non-nil, zero value otherwise.

### GetOsLikeOk

`func (o *NodePage) GetOsLikeOk() (*string, bool)`

GetOsLikeOk returns a tuple with the OsLike field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOsLike

`func (o *NodePage) SetOsLike(v string)`

SetOsLike sets OsLike field to given value.


### GetOsName

`func (o *NodePage) GetOsName() string`

GetOsName returns the OsName field if non-nil, zero value otherwise.

### GetOsNameOk

`func (o *NodePage) GetOsNameOk() (*string, bool)`

GetOsNameOk returns a tuple with the OsName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOsName

`func (o *NodePage) SetOsName(v string)`

SetOsName sets OsName field to given value.


### GetOsVersion

`func (o *NodePage) GetOsVersion() string`

GetOsVersion returns the OsVersion field if non-nil, zero value otherwise.

### GetOsVersionOk

`func (o *NodePage) GetOsVersionOk() (*string, bool)`

GetOsVersionOk returns a tuple with the OsVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOsVersion

`func (o *NodePage) SetOsVersion(v string)`

SetOsVersion sets OsVersion field to given value.


### GetStatus

`func (o *NodePage) GetStatus() int32`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *NodePage) GetStatusOk() (*int32, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *NodePage) SetStatus(v int32)`

SetStatus sets Status field to given value.


### GetQemuVersion

`func (o *NodePage) GetQemuVersion() string`

GetQemuVersion returns the QemuVersion field if non-nil, zero value otherwise.

### GetQemuVersionOk

`func (o *NodePage) GetQemuVersionOk() (*string, bool)`

GetQemuVersionOk returns a tuple with the QemuVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetQemuVersion

`func (o *NodePage) SetQemuVersion(v string)`

SetQemuVersion sets QemuVersion field to given value.

### HasQemuVersion

`func (o *NodePage) HasQemuVersion() bool`

HasQemuVersion returns a boolean if a field has been set.

### GetLibvirtVersion

`func (o *NodePage) GetLibvirtVersion() string`

GetLibvirtVersion returns the LibvirtVersion field if non-nil, zero value otherwise.

### GetLibvirtVersionOk

`func (o *NodePage) GetLibvirtVersionOk() (*string, bool)`

GetLibvirtVersionOk returns a tuple with the LibvirtVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLibvirtVersion

`func (o *NodePage) SetLibvirtVersion(v string)`

SetLibvirtVersion sets LibvirtVersion field to given value.

### HasLibvirtVersion

`func (o *NodePage) HasLibvirtVersion() bool`

HasLibvirtVersion returns a boolean if a field has been set.

### GetRoles

`func (o *NodePage) GetRoles() []NodeRole`

GetRoles returns the Roles field if non-nil, zero value otherwise.

### GetRolesOk

`func (o *NodePage) GetRolesOk() (*[]NodeRole, bool)`

GetRolesOk returns a tuple with the Roles field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRoles

`func (o *NodePage) SetRoles(v []NodeRole)`

SetRoles sets Roles field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


