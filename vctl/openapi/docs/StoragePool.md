# StoragePool

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **int32** |  | 
**Name** | **string** |  | 
**Storages** | [**[]StorageContainerForStoragePool**](StorageContainerForStoragePool.md) |  | 

## Methods

### NewStoragePool

`func NewStoragePool(id int32, name string, storages []StorageContainerForStoragePool, ) *StoragePool`

NewStoragePool instantiates a new StoragePool object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStoragePoolWithDefaults

`func NewStoragePoolWithDefaults() *StoragePool`

NewStoragePoolWithDefaults instantiates a new StoragePool object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *StoragePool) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *StoragePool) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *StoragePool) SetId(v int32)`

SetId sets Id field to given value.


### GetName

`func (o *StoragePool) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *StoragePool) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *StoragePool) SetName(v string)`

SetName sets Name field to given value.


### GetStorages

`func (o *StoragePool) GetStorages() []StorageContainerForStoragePool`

GetStorages returns the Storages field if non-nil, zero value otherwise.

### GetStoragesOk

`func (o *StoragePool) GetStoragesOk() (*[]StorageContainerForStoragePool, bool)`

GetStoragesOk returns a tuple with the Storages field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStorages

`func (o *StoragePool) SetStorages(v []StorageContainerForStoragePool)`

SetStorages sets Storages field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


