# ImageDomain

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**OwnerUserId** | Pointer to **string** |  | [optional] 
**IssuanceId** | Pointer to **int32** |  | [optional] 
**Name** | **string** |  | 
**Uuid** | **string** |  | 

## Methods

### NewImageDomain

`func NewImageDomain(name string, uuid string, ) *ImageDomain`

NewImageDomain instantiates a new ImageDomain object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewImageDomainWithDefaults

`func NewImageDomainWithDefaults() *ImageDomain`

NewImageDomainWithDefaults instantiates a new ImageDomain object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetOwnerUserId

`func (o *ImageDomain) GetOwnerUserId() string`

GetOwnerUserId returns the OwnerUserId field if non-nil, zero value otherwise.

### GetOwnerUserIdOk

`func (o *ImageDomain) GetOwnerUserIdOk() (*string, bool)`

GetOwnerUserIdOk returns a tuple with the OwnerUserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOwnerUserId

`func (o *ImageDomain) SetOwnerUserId(v string)`

SetOwnerUserId sets OwnerUserId field to given value.

### HasOwnerUserId

`func (o *ImageDomain) HasOwnerUserId() bool`

HasOwnerUserId returns a boolean if a field has been set.

### GetIssuanceId

`func (o *ImageDomain) GetIssuanceId() int32`

GetIssuanceId returns the IssuanceId field if non-nil, zero value otherwise.

### GetIssuanceIdOk

`func (o *ImageDomain) GetIssuanceIdOk() (*int32, bool)`

GetIssuanceIdOk returns a tuple with the IssuanceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIssuanceId

`func (o *ImageDomain) SetIssuanceId(v int32)`

SetIssuanceId sets IssuanceId field to given value.

### HasIssuanceId

`func (o *ImageDomain) HasIssuanceId() bool`

HasIssuanceId returns a boolean if a field has been set.

### GetName

`func (o *ImageDomain) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *ImageDomain) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *ImageDomain) SetName(v string)`

SetName sets Name field to given value.


### GetUuid

`func (o *ImageDomain) GetUuid() string`

GetUuid returns the Uuid field if non-nil, zero value otherwise.

### GetUuidOk

`func (o *ImageDomain) GetUuidOk() (*string, bool)`

GetUuidOk returns a tuple with the Uuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUuid

`func (o *ImageDomain) SetUuid(v string)`

SetUuid sets Uuid field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


