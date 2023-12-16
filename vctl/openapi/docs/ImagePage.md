# ImagePage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**StorageUuid** | Pointer to **string** |  | [optional] 
**Capacity** | **int32** |  | 
**Storage** | [**StoragePage**](StoragePage.md) |  | 
**Flavor** | Pointer to [**Flavor**](Flavor.md) |  | [optional] 
**Allocation** | **int32** |  | 
**Path** | **string** |  | 
**UpdateToken** | Pointer to **string** |  | [optional] 
**Domain** | Pointer to [**ImageDomain**](ImageDomain.md) |  | [optional] 

## Methods

### NewImagePage

`func NewImagePage(name string, capacity int32, storage StoragePage, allocation int32, path string, ) *ImagePage`

NewImagePage instantiates a new ImagePage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewImagePageWithDefaults

`func NewImagePageWithDefaults() *ImagePage`

NewImagePageWithDefaults instantiates a new ImagePage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *ImagePage) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *ImagePage) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *ImagePage) SetName(v string)`

SetName sets Name field to given value.


### GetStorageUuid

`func (o *ImagePage) GetStorageUuid() string`

GetStorageUuid returns the StorageUuid field if non-nil, zero value otherwise.

### GetStorageUuidOk

`func (o *ImagePage) GetStorageUuidOk() (*string, bool)`

GetStorageUuidOk returns a tuple with the StorageUuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStorageUuid

`func (o *ImagePage) SetStorageUuid(v string)`

SetStorageUuid sets StorageUuid field to given value.

### HasStorageUuid

`func (o *ImagePage) HasStorageUuid() bool`

HasStorageUuid returns a boolean if a field has been set.

### GetCapacity

`func (o *ImagePage) GetCapacity() int32`

GetCapacity returns the Capacity field if non-nil, zero value otherwise.

### GetCapacityOk

`func (o *ImagePage) GetCapacityOk() (*int32, bool)`

GetCapacityOk returns a tuple with the Capacity field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCapacity

`func (o *ImagePage) SetCapacity(v int32)`

SetCapacity sets Capacity field to given value.


### GetStorage

`func (o *ImagePage) GetStorage() StoragePage`

GetStorage returns the Storage field if non-nil, zero value otherwise.

### GetStorageOk

`func (o *ImagePage) GetStorageOk() (*StoragePage, bool)`

GetStorageOk returns a tuple with the Storage field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStorage

`func (o *ImagePage) SetStorage(v StoragePage)`

SetStorage sets Storage field to given value.


### GetFlavor

`func (o *ImagePage) GetFlavor() Flavor`

GetFlavor returns the Flavor field if non-nil, zero value otherwise.

### GetFlavorOk

`func (o *ImagePage) GetFlavorOk() (*Flavor, bool)`

GetFlavorOk returns a tuple with the Flavor field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFlavor

`func (o *ImagePage) SetFlavor(v Flavor)`

SetFlavor sets Flavor field to given value.

### HasFlavor

`func (o *ImagePage) HasFlavor() bool`

HasFlavor returns a boolean if a field has been set.

### GetAllocation

`func (o *ImagePage) GetAllocation() int32`

GetAllocation returns the Allocation field if non-nil, zero value otherwise.

### GetAllocationOk

`func (o *ImagePage) GetAllocationOk() (*int32, bool)`

GetAllocationOk returns a tuple with the Allocation field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAllocation

`func (o *ImagePage) SetAllocation(v int32)`

SetAllocation sets Allocation field to given value.


### GetPath

`func (o *ImagePage) GetPath() string`

GetPath returns the Path field if non-nil, zero value otherwise.

### GetPathOk

`func (o *ImagePage) GetPathOk() (*string, bool)`

GetPathOk returns a tuple with the Path field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPath

`func (o *ImagePage) SetPath(v string)`

SetPath sets Path field to given value.


### GetUpdateToken

`func (o *ImagePage) GetUpdateToken() string`

GetUpdateToken returns the UpdateToken field if non-nil, zero value otherwise.

### GetUpdateTokenOk

`func (o *ImagePage) GetUpdateTokenOk() (*string, bool)`

GetUpdateTokenOk returns a tuple with the UpdateToken field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUpdateToken

`func (o *ImagePage) SetUpdateToken(v string)`

SetUpdateToken sets UpdateToken field to given value.

### HasUpdateToken

`func (o *ImagePage) HasUpdateToken() bool`

HasUpdateToken returns a boolean if a field has been set.

### GetDomain

`func (o *ImagePage) GetDomain() ImageDomain`

GetDomain returns the Domain field if non-nil, zero value otherwise.

### GetDomainOk

`func (o *ImagePage) GetDomainOk() (*ImageDomain, bool)`

GetDomainOk returns a tuple with the Domain field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDomain

`func (o *ImagePage) SetDomain(v ImageDomain)`

SetDomain sets Domain field to given value.

### HasDomain

`func (o *ImagePage) HasDomain() bool`

HasDomain returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


