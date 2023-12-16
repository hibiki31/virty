# StoragePoolForCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**StorageUuids** | **[]string** |  | 

## Methods

### NewStoragePoolForCreate

`func NewStoragePoolForCreate(name string, storageUuids []string, ) *StoragePoolForCreate`

NewStoragePoolForCreate instantiates a new StoragePoolForCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStoragePoolForCreateWithDefaults

`func NewStoragePoolForCreateWithDefaults() *StoragePoolForCreate`

NewStoragePoolForCreateWithDefaults instantiates a new StoragePoolForCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *StoragePoolForCreate) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *StoragePoolForCreate) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *StoragePoolForCreate) SetName(v string)`

SetName sets Name field to given value.


### GetStorageUuids

`func (o *StoragePoolForCreate) GetStorageUuids() []string`

GetStorageUuids returns the StorageUuids field if non-nil, zero value otherwise.

### GetStorageUuidsOk

`func (o *StoragePoolForCreate) GetStorageUuidsOk() (*[]string, bool)`

GetStorageUuidsOk returns a tuple with the StorageUuids field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStorageUuids

`func (o *StoragePoolForCreate) SetStorageUuids(v []string)`

SetStorageUuids sets StorageUuids field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


