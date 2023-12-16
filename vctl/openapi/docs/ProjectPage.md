# ProjectPage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Name** | **string** |  | 
**MemoryG** | **int32** |  | 
**Core** | **int32** |  | 
**StorageCapacityG** | **int32** |  | 
**Users** | [**[]ProjectUser**](ProjectUser.md) |  | 
**UsedMemoryG** | **int32** |  | 
**UsedCore** | **int32** |  | 
**NetworkPools** | Pointer to **interface{}** |  | [optional] 
**StoragePools** | Pointer to **interface{}** |  | [optional] 

## Methods

### NewProjectPage

`func NewProjectPage(id string, name string, memoryG int32, core int32, storageCapacityG int32, users []ProjectUser, usedMemoryG int32, usedCore int32, ) *ProjectPage`

NewProjectPage instantiates a new ProjectPage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewProjectPageWithDefaults

`func NewProjectPageWithDefaults() *ProjectPage`

NewProjectPageWithDefaults instantiates a new ProjectPage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *ProjectPage) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *ProjectPage) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *ProjectPage) SetId(v string)`

SetId sets Id field to given value.


### GetName

`func (o *ProjectPage) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *ProjectPage) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *ProjectPage) SetName(v string)`

SetName sets Name field to given value.


### GetMemoryG

`func (o *ProjectPage) GetMemoryG() int32`

GetMemoryG returns the MemoryG field if non-nil, zero value otherwise.

### GetMemoryGOk

`func (o *ProjectPage) GetMemoryGOk() (*int32, bool)`

GetMemoryGOk returns a tuple with the MemoryG field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemoryG

`func (o *ProjectPage) SetMemoryG(v int32)`

SetMemoryG sets MemoryG field to given value.


### GetCore

`func (o *ProjectPage) GetCore() int32`

GetCore returns the Core field if non-nil, zero value otherwise.

### GetCoreOk

`func (o *ProjectPage) GetCoreOk() (*int32, bool)`

GetCoreOk returns a tuple with the Core field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCore

`func (o *ProjectPage) SetCore(v int32)`

SetCore sets Core field to given value.


### GetStorageCapacityG

`func (o *ProjectPage) GetStorageCapacityG() int32`

GetStorageCapacityG returns the StorageCapacityG field if non-nil, zero value otherwise.

### GetStorageCapacityGOk

`func (o *ProjectPage) GetStorageCapacityGOk() (*int32, bool)`

GetStorageCapacityGOk returns a tuple with the StorageCapacityG field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStorageCapacityG

`func (o *ProjectPage) SetStorageCapacityG(v int32)`

SetStorageCapacityG sets StorageCapacityG field to given value.


### GetUsers

`func (o *ProjectPage) GetUsers() []ProjectUser`

GetUsers returns the Users field if non-nil, zero value otherwise.

### GetUsersOk

`func (o *ProjectPage) GetUsersOk() (*[]ProjectUser, bool)`

GetUsersOk returns a tuple with the Users field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsers

`func (o *ProjectPage) SetUsers(v []ProjectUser)`

SetUsers sets Users field to given value.


### GetUsedMemoryG

`func (o *ProjectPage) GetUsedMemoryG() int32`

GetUsedMemoryG returns the UsedMemoryG field if non-nil, zero value otherwise.

### GetUsedMemoryGOk

`func (o *ProjectPage) GetUsedMemoryGOk() (*int32, bool)`

GetUsedMemoryGOk returns a tuple with the UsedMemoryG field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsedMemoryG

`func (o *ProjectPage) SetUsedMemoryG(v int32)`

SetUsedMemoryG sets UsedMemoryG field to given value.


### GetUsedCore

`func (o *ProjectPage) GetUsedCore() int32`

GetUsedCore returns the UsedCore field if non-nil, zero value otherwise.

### GetUsedCoreOk

`func (o *ProjectPage) GetUsedCoreOk() (*int32, bool)`

GetUsedCoreOk returns a tuple with the UsedCore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsedCore

`func (o *ProjectPage) SetUsedCore(v int32)`

SetUsedCore sets UsedCore field to given value.


### GetNetworkPools

`func (o *ProjectPage) GetNetworkPools() interface{}`

GetNetworkPools returns the NetworkPools field if non-nil, zero value otherwise.

### GetNetworkPoolsOk

`func (o *ProjectPage) GetNetworkPoolsOk() (*interface{}, bool)`

GetNetworkPoolsOk returns a tuple with the NetworkPools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNetworkPools

`func (o *ProjectPage) SetNetworkPools(v interface{})`

SetNetworkPools sets NetworkPools field to given value.

### HasNetworkPools

`func (o *ProjectPage) HasNetworkPools() bool`

HasNetworkPools returns a boolean if a field has been set.

### SetNetworkPoolsNil

`func (o *ProjectPage) SetNetworkPoolsNil(b bool)`

 SetNetworkPoolsNil sets the value for NetworkPools to be an explicit nil

### UnsetNetworkPools
`func (o *ProjectPage) UnsetNetworkPools()`

UnsetNetworkPools ensures that no value is present for NetworkPools, not even an explicit nil
### GetStoragePools

`func (o *ProjectPage) GetStoragePools() interface{}`

GetStoragePools returns the StoragePools field if non-nil, zero value otherwise.

### GetStoragePoolsOk

`func (o *ProjectPage) GetStoragePoolsOk() (*interface{}, bool)`

GetStoragePoolsOk returns a tuple with the StoragePools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStoragePools

`func (o *ProjectPage) SetStoragePools(v interface{})`

SetStoragePools sets StoragePools field to given value.

### HasStoragePools

`func (o *ProjectPage) HasStoragePools() bool`

HasStoragePools returns a boolean if a field has been set.

### SetStoragePoolsNil

`func (o *ProjectPage) SetStoragePoolsNil(b bool)`

 SetStoragePoolsNil sets the value for StoragePools to be an explicit nil

### UnsetStoragePools
`func (o *ProjectPage) UnsetStoragePools()`

UnsetStoragePools ensures that no value is present for StoragePools, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


