# Domain

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Uuid** | **string** |  | 
**Name** | **string** |  | 
**Core** | **int32** |  | 
**Memory** | **int32** |  | 
**Status** | **int32** |  | 
**Description** | Pointer to **string** |  | [optional] 
**NodeName** | **string** |  | 
**OwnerUserId** | Pointer to **string** |  | [optional] 
**OwnerProjectId** | Pointer to **string** |  | [optional] 
**OwnerProject** | Pointer to [**DomainProject**](DomainProject.md) |  | [optional] 
**VncPort** | Pointer to **int32** |  | [optional] 
**VncPassword** | Pointer to **string** |  | [optional] 
**Drives** | Pointer to [**[]DomainDrive**](DomainDrive.md) |  | [optional] 
**Interfaces** | Pointer to [**[]DomainInterface**](DomainInterface.md) |  | [optional] 

## Methods

### NewDomain

`func NewDomain(uuid string, name string, core int32, memory int32, status int32, nodeName string, ) *Domain`

NewDomain instantiates a new Domain object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDomainWithDefaults

`func NewDomainWithDefaults() *Domain`

NewDomainWithDefaults instantiates a new Domain object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetUuid

`func (o *Domain) GetUuid() string`

GetUuid returns the Uuid field if non-nil, zero value otherwise.

### GetUuidOk

`func (o *Domain) GetUuidOk() (*string, bool)`

GetUuidOk returns a tuple with the Uuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUuid

`func (o *Domain) SetUuid(v string)`

SetUuid sets Uuid field to given value.


### GetName

`func (o *Domain) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *Domain) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *Domain) SetName(v string)`

SetName sets Name field to given value.


### GetCore

`func (o *Domain) GetCore() int32`

GetCore returns the Core field if non-nil, zero value otherwise.

### GetCoreOk

`func (o *Domain) GetCoreOk() (*int32, bool)`

GetCoreOk returns a tuple with the Core field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCore

`func (o *Domain) SetCore(v int32)`

SetCore sets Core field to given value.


### GetMemory

`func (o *Domain) GetMemory() int32`

GetMemory returns the Memory field if non-nil, zero value otherwise.

### GetMemoryOk

`func (o *Domain) GetMemoryOk() (*int32, bool)`

GetMemoryOk returns a tuple with the Memory field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemory

`func (o *Domain) SetMemory(v int32)`

SetMemory sets Memory field to given value.


### GetStatus

`func (o *Domain) GetStatus() int32`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *Domain) GetStatusOk() (*int32, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *Domain) SetStatus(v int32)`

SetStatus sets Status field to given value.


### GetDescription

`func (o *Domain) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *Domain) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *Domain) SetDescription(v string)`

SetDescription sets Description field to given value.

### HasDescription

`func (o *Domain) HasDescription() bool`

HasDescription returns a boolean if a field has been set.

### GetNodeName

`func (o *Domain) GetNodeName() string`

GetNodeName returns the NodeName field if non-nil, zero value otherwise.

### GetNodeNameOk

`func (o *Domain) GetNodeNameOk() (*string, bool)`

GetNodeNameOk returns a tuple with the NodeName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNodeName

`func (o *Domain) SetNodeName(v string)`

SetNodeName sets NodeName field to given value.


### GetOwnerUserId

`func (o *Domain) GetOwnerUserId() string`

GetOwnerUserId returns the OwnerUserId field if non-nil, zero value otherwise.

### GetOwnerUserIdOk

`func (o *Domain) GetOwnerUserIdOk() (*string, bool)`

GetOwnerUserIdOk returns a tuple with the OwnerUserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOwnerUserId

`func (o *Domain) SetOwnerUserId(v string)`

SetOwnerUserId sets OwnerUserId field to given value.

### HasOwnerUserId

`func (o *Domain) HasOwnerUserId() bool`

HasOwnerUserId returns a boolean if a field has been set.

### GetOwnerProjectId

`func (o *Domain) GetOwnerProjectId() string`

GetOwnerProjectId returns the OwnerProjectId field if non-nil, zero value otherwise.

### GetOwnerProjectIdOk

`func (o *Domain) GetOwnerProjectIdOk() (*string, bool)`

GetOwnerProjectIdOk returns a tuple with the OwnerProjectId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOwnerProjectId

`func (o *Domain) SetOwnerProjectId(v string)`

SetOwnerProjectId sets OwnerProjectId field to given value.

### HasOwnerProjectId

`func (o *Domain) HasOwnerProjectId() bool`

HasOwnerProjectId returns a boolean if a field has been set.

### GetOwnerProject

`func (o *Domain) GetOwnerProject() DomainProject`

GetOwnerProject returns the OwnerProject field if non-nil, zero value otherwise.

### GetOwnerProjectOk

`func (o *Domain) GetOwnerProjectOk() (*DomainProject, bool)`

GetOwnerProjectOk returns a tuple with the OwnerProject field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOwnerProject

`func (o *Domain) SetOwnerProject(v DomainProject)`

SetOwnerProject sets OwnerProject field to given value.

### HasOwnerProject

`func (o *Domain) HasOwnerProject() bool`

HasOwnerProject returns a boolean if a field has been set.

### GetVncPort

`func (o *Domain) GetVncPort() int32`

GetVncPort returns the VncPort field if non-nil, zero value otherwise.

### GetVncPortOk

`func (o *Domain) GetVncPortOk() (*int32, bool)`

GetVncPortOk returns a tuple with the VncPort field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVncPort

`func (o *Domain) SetVncPort(v int32)`

SetVncPort sets VncPort field to given value.

### HasVncPort

`func (o *Domain) HasVncPort() bool`

HasVncPort returns a boolean if a field has been set.

### GetVncPassword

`func (o *Domain) GetVncPassword() string`

GetVncPassword returns the VncPassword field if non-nil, zero value otherwise.

### GetVncPasswordOk

`func (o *Domain) GetVncPasswordOk() (*string, bool)`

GetVncPasswordOk returns a tuple with the VncPassword field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVncPassword

`func (o *Domain) SetVncPassword(v string)`

SetVncPassword sets VncPassword field to given value.

### HasVncPassword

`func (o *Domain) HasVncPassword() bool`

HasVncPassword returns a boolean if a field has been set.

### GetDrives

`func (o *Domain) GetDrives() []DomainDrive`

GetDrives returns the Drives field if non-nil, zero value otherwise.

### GetDrivesOk

`func (o *Domain) GetDrivesOk() (*[]DomainDrive, bool)`

GetDrivesOk returns a tuple with the Drives field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDrives

`func (o *Domain) SetDrives(v []DomainDrive)`

SetDrives sets Drives field to given value.

### HasDrives

`func (o *Domain) HasDrives() bool`

HasDrives returns a boolean if a field has been set.

### GetInterfaces

`func (o *Domain) GetInterfaces() []DomainInterface`

GetInterfaces returns the Interfaces field if non-nil, zero value otherwise.

### GetInterfacesOk

`func (o *Domain) GetInterfacesOk() (*[]DomainInterface, bool)`

GetInterfacesOk returns a tuple with the Interfaces field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInterfaces

`func (o *Domain) SetInterfaces(v []DomainInterface)`

SetInterfaces sets Interfaces field to given value.

### HasInterfaces

`func (o *Domain) HasInterfaces() bool`

HasInterfaces returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


