# DomainDetail

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
**Node** | [**Node**](Node.md) |  | 

## Methods

### NewDomainDetail

`func NewDomainDetail(uuid string, name string, core int32, memory int32, status int32, nodeName string, node Node, ) *DomainDetail`

NewDomainDetail instantiates a new DomainDetail object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDomainDetailWithDefaults

`func NewDomainDetailWithDefaults() *DomainDetail`

NewDomainDetailWithDefaults instantiates a new DomainDetail object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetUuid

`func (o *DomainDetail) GetUuid() string`

GetUuid returns the Uuid field if non-nil, zero value otherwise.

### GetUuidOk

`func (o *DomainDetail) GetUuidOk() (*string, bool)`

GetUuidOk returns a tuple with the Uuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUuid

`func (o *DomainDetail) SetUuid(v string)`

SetUuid sets Uuid field to given value.


### GetName

`func (o *DomainDetail) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *DomainDetail) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *DomainDetail) SetName(v string)`

SetName sets Name field to given value.


### GetCore

`func (o *DomainDetail) GetCore() int32`

GetCore returns the Core field if non-nil, zero value otherwise.

### GetCoreOk

`func (o *DomainDetail) GetCoreOk() (*int32, bool)`

GetCoreOk returns a tuple with the Core field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCore

`func (o *DomainDetail) SetCore(v int32)`

SetCore sets Core field to given value.


### GetMemory

`func (o *DomainDetail) GetMemory() int32`

GetMemory returns the Memory field if non-nil, zero value otherwise.

### GetMemoryOk

`func (o *DomainDetail) GetMemoryOk() (*int32, bool)`

GetMemoryOk returns a tuple with the Memory field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemory

`func (o *DomainDetail) SetMemory(v int32)`

SetMemory sets Memory field to given value.


### GetStatus

`func (o *DomainDetail) GetStatus() int32`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *DomainDetail) GetStatusOk() (*int32, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *DomainDetail) SetStatus(v int32)`

SetStatus sets Status field to given value.


### GetDescription

`func (o *DomainDetail) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *DomainDetail) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *DomainDetail) SetDescription(v string)`

SetDescription sets Description field to given value.

### HasDescription

`func (o *DomainDetail) HasDescription() bool`

HasDescription returns a boolean if a field has been set.

### GetNodeName

`func (o *DomainDetail) GetNodeName() string`

GetNodeName returns the NodeName field if non-nil, zero value otherwise.

### GetNodeNameOk

`func (o *DomainDetail) GetNodeNameOk() (*string, bool)`

GetNodeNameOk returns a tuple with the NodeName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNodeName

`func (o *DomainDetail) SetNodeName(v string)`

SetNodeName sets NodeName field to given value.


### GetOwnerUserId

`func (o *DomainDetail) GetOwnerUserId() string`

GetOwnerUserId returns the OwnerUserId field if non-nil, zero value otherwise.

### GetOwnerUserIdOk

`func (o *DomainDetail) GetOwnerUserIdOk() (*string, bool)`

GetOwnerUserIdOk returns a tuple with the OwnerUserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOwnerUserId

`func (o *DomainDetail) SetOwnerUserId(v string)`

SetOwnerUserId sets OwnerUserId field to given value.

### HasOwnerUserId

`func (o *DomainDetail) HasOwnerUserId() bool`

HasOwnerUserId returns a boolean if a field has been set.

### GetOwnerProjectId

`func (o *DomainDetail) GetOwnerProjectId() string`

GetOwnerProjectId returns the OwnerProjectId field if non-nil, zero value otherwise.

### GetOwnerProjectIdOk

`func (o *DomainDetail) GetOwnerProjectIdOk() (*string, bool)`

GetOwnerProjectIdOk returns a tuple with the OwnerProjectId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOwnerProjectId

`func (o *DomainDetail) SetOwnerProjectId(v string)`

SetOwnerProjectId sets OwnerProjectId field to given value.

### HasOwnerProjectId

`func (o *DomainDetail) HasOwnerProjectId() bool`

HasOwnerProjectId returns a boolean if a field has been set.

### GetOwnerProject

`func (o *DomainDetail) GetOwnerProject() DomainProject`

GetOwnerProject returns the OwnerProject field if non-nil, zero value otherwise.

### GetOwnerProjectOk

`func (o *DomainDetail) GetOwnerProjectOk() (*DomainProject, bool)`

GetOwnerProjectOk returns a tuple with the OwnerProject field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOwnerProject

`func (o *DomainDetail) SetOwnerProject(v DomainProject)`

SetOwnerProject sets OwnerProject field to given value.

### HasOwnerProject

`func (o *DomainDetail) HasOwnerProject() bool`

HasOwnerProject returns a boolean if a field has been set.

### GetVncPort

`func (o *DomainDetail) GetVncPort() int32`

GetVncPort returns the VncPort field if non-nil, zero value otherwise.

### GetVncPortOk

`func (o *DomainDetail) GetVncPortOk() (*int32, bool)`

GetVncPortOk returns a tuple with the VncPort field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVncPort

`func (o *DomainDetail) SetVncPort(v int32)`

SetVncPort sets VncPort field to given value.

### HasVncPort

`func (o *DomainDetail) HasVncPort() bool`

HasVncPort returns a boolean if a field has been set.

### GetVncPassword

`func (o *DomainDetail) GetVncPassword() string`

GetVncPassword returns the VncPassword field if non-nil, zero value otherwise.

### GetVncPasswordOk

`func (o *DomainDetail) GetVncPasswordOk() (*string, bool)`

GetVncPasswordOk returns a tuple with the VncPassword field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVncPassword

`func (o *DomainDetail) SetVncPassword(v string)`

SetVncPassword sets VncPassword field to given value.

### HasVncPassword

`func (o *DomainDetail) HasVncPassword() bool`

HasVncPassword returns a boolean if a field has been set.

### GetDrives

`func (o *DomainDetail) GetDrives() []DomainDrive`

GetDrives returns the Drives field if non-nil, zero value otherwise.

### GetDrivesOk

`func (o *DomainDetail) GetDrivesOk() (*[]DomainDrive, bool)`

GetDrivesOk returns a tuple with the Drives field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDrives

`func (o *DomainDetail) SetDrives(v []DomainDrive)`

SetDrives sets Drives field to given value.

### HasDrives

`func (o *DomainDetail) HasDrives() bool`

HasDrives returns a boolean if a field has been set.

### GetInterfaces

`func (o *DomainDetail) GetInterfaces() []DomainInterface`

GetInterfaces returns the Interfaces field if non-nil, zero value otherwise.

### GetInterfacesOk

`func (o *DomainDetail) GetInterfacesOk() (*[]DomainInterface, bool)`

GetInterfacesOk returns a tuple with the Interfaces field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInterfaces

`func (o *DomainDetail) SetInterfaces(v []DomainInterface)`

SetInterfaces sets Interfaces field to given value.

### HasInterfaces

`func (o *DomainDetail) HasInterfaces() bool`

HasInterfaces returns a boolean if a field has been set.

### GetNode

`func (o *DomainDetail) GetNode() Node`

GetNode returns the Node field if non-nil, zero value otherwise.

### GetNodeOk

`func (o *DomainDetail) GetNodeOk() (*Node, bool)`

GetNodeOk returns a tuple with the Node field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNode

`func (o *DomainDetail) SetNode(v Node)`

SetNode sets Node field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


