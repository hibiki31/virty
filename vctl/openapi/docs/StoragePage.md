# StoragePage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**Uuid** | **string** |  | 
**Status** | **int32** |  | 
**Active** | **bool** |  | 
**Available** | Pointer to **int32** |  | [optional] 
**Capacity** | Pointer to **int32** |  | [optional] 
**NodeName** | **string** |  | 
**Node** | [**NodePage**](NodePage.md) |  | 
**AutoStart** | **bool** |  | 
**Path** | Pointer to **string** |  | [optional] 
**MetaData** | Pointer to [**StorageMetadata**](StorageMetadata.md) |  | [optional] 
**UpdateToken** | Pointer to **string** |  | [optional] 
**AllocationCommit** | Pointer to **int32** |  | [optional] 
**CapacityCommit** | Pointer to **int32** |  | [optional] 

## Methods

### NewStoragePage

`func NewStoragePage(name string, uuid string, status int32, active bool, nodeName string, node NodePage, autoStart bool, ) *StoragePage`

NewStoragePage instantiates a new StoragePage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStoragePageWithDefaults

`func NewStoragePageWithDefaults() *StoragePage`

NewStoragePageWithDefaults instantiates a new StoragePage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *StoragePage) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *StoragePage) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *StoragePage) SetName(v string)`

SetName sets Name field to given value.


### GetUuid

`func (o *StoragePage) GetUuid() string`

GetUuid returns the Uuid field if non-nil, zero value otherwise.

### GetUuidOk

`func (o *StoragePage) GetUuidOk() (*string, bool)`

GetUuidOk returns a tuple with the Uuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUuid

`func (o *StoragePage) SetUuid(v string)`

SetUuid sets Uuid field to given value.


### GetStatus

`func (o *StoragePage) GetStatus() int32`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *StoragePage) GetStatusOk() (*int32, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *StoragePage) SetStatus(v int32)`

SetStatus sets Status field to given value.


### GetActive

`func (o *StoragePage) GetActive() bool`

GetActive returns the Active field if non-nil, zero value otherwise.

### GetActiveOk

`func (o *StoragePage) GetActiveOk() (*bool, bool)`

GetActiveOk returns a tuple with the Active field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActive

`func (o *StoragePage) SetActive(v bool)`

SetActive sets Active field to given value.


### GetAvailable

`func (o *StoragePage) GetAvailable() int32`

GetAvailable returns the Available field if non-nil, zero value otherwise.

### GetAvailableOk

`func (o *StoragePage) GetAvailableOk() (*int32, bool)`

GetAvailableOk returns a tuple with the Available field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAvailable

`func (o *StoragePage) SetAvailable(v int32)`

SetAvailable sets Available field to given value.

### HasAvailable

`func (o *StoragePage) HasAvailable() bool`

HasAvailable returns a boolean if a field has been set.

### GetCapacity

`func (o *StoragePage) GetCapacity() int32`

GetCapacity returns the Capacity field if non-nil, zero value otherwise.

### GetCapacityOk

`func (o *StoragePage) GetCapacityOk() (*int32, bool)`

GetCapacityOk returns a tuple with the Capacity field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCapacity

`func (o *StoragePage) SetCapacity(v int32)`

SetCapacity sets Capacity field to given value.

### HasCapacity

`func (o *StoragePage) HasCapacity() bool`

HasCapacity returns a boolean if a field has been set.

### GetNodeName

`func (o *StoragePage) GetNodeName() string`

GetNodeName returns the NodeName field if non-nil, zero value otherwise.

### GetNodeNameOk

`func (o *StoragePage) GetNodeNameOk() (*string, bool)`

GetNodeNameOk returns a tuple with the NodeName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNodeName

`func (o *StoragePage) SetNodeName(v string)`

SetNodeName sets NodeName field to given value.


### GetNode

`func (o *StoragePage) GetNode() NodePage`

GetNode returns the Node field if non-nil, zero value otherwise.

### GetNodeOk

`func (o *StoragePage) GetNodeOk() (*NodePage, bool)`

GetNodeOk returns a tuple with the Node field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNode

`func (o *StoragePage) SetNode(v NodePage)`

SetNode sets Node field to given value.


### GetAutoStart

`func (o *StoragePage) GetAutoStart() bool`

GetAutoStart returns the AutoStart field if non-nil, zero value otherwise.

### GetAutoStartOk

`func (o *StoragePage) GetAutoStartOk() (*bool, bool)`

GetAutoStartOk returns a tuple with the AutoStart field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAutoStart

`func (o *StoragePage) SetAutoStart(v bool)`

SetAutoStart sets AutoStart field to given value.


### GetPath

`func (o *StoragePage) GetPath() string`

GetPath returns the Path field if non-nil, zero value otherwise.

### GetPathOk

`func (o *StoragePage) GetPathOk() (*string, bool)`

GetPathOk returns a tuple with the Path field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPath

`func (o *StoragePage) SetPath(v string)`

SetPath sets Path field to given value.

### HasPath

`func (o *StoragePage) HasPath() bool`

HasPath returns a boolean if a field has been set.

### GetMetaData

`func (o *StoragePage) GetMetaData() StorageMetadata`

GetMetaData returns the MetaData field if non-nil, zero value otherwise.

### GetMetaDataOk

`func (o *StoragePage) GetMetaDataOk() (*StorageMetadata, bool)`

GetMetaDataOk returns a tuple with the MetaData field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetaData

`func (o *StoragePage) SetMetaData(v StorageMetadata)`

SetMetaData sets MetaData field to given value.

### HasMetaData

`func (o *StoragePage) HasMetaData() bool`

HasMetaData returns a boolean if a field has been set.

### GetUpdateToken

`func (o *StoragePage) GetUpdateToken() string`

GetUpdateToken returns the UpdateToken field if non-nil, zero value otherwise.

### GetUpdateTokenOk

`func (o *StoragePage) GetUpdateTokenOk() (*string, bool)`

GetUpdateTokenOk returns a tuple with the UpdateToken field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUpdateToken

`func (o *StoragePage) SetUpdateToken(v string)`

SetUpdateToken sets UpdateToken field to given value.

### HasUpdateToken

`func (o *StoragePage) HasUpdateToken() bool`

HasUpdateToken returns a boolean if a field has been set.

### GetAllocationCommit

`func (o *StoragePage) GetAllocationCommit() int32`

GetAllocationCommit returns the AllocationCommit field if non-nil, zero value otherwise.

### GetAllocationCommitOk

`func (o *StoragePage) GetAllocationCommitOk() (*int32, bool)`

GetAllocationCommitOk returns a tuple with the AllocationCommit field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAllocationCommit

`func (o *StoragePage) SetAllocationCommit(v int32)`

SetAllocationCommit sets AllocationCommit field to given value.

### HasAllocationCommit

`func (o *StoragePage) HasAllocationCommit() bool`

HasAllocationCommit returns a boolean if a field has been set.

### GetCapacityCommit

`func (o *StoragePage) GetCapacityCommit() int32`

GetCapacityCommit returns the CapacityCommit field if non-nil, zero value otherwise.

### GetCapacityCommitOk

`func (o *StoragePage) GetCapacityCommitOk() (*int32, bool)`

GetCapacityCommitOk returns a tuple with the CapacityCommit field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCapacityCommit

`func (o *StoragePage) SetCapacityCommit(v int32)`

SetCapacityCommit sets CapacityCommit field to given value.

### HasCapacityCommit

`func (o *StoragePage) HasCapacityCommit() bool`

HasCapacityCommit returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


