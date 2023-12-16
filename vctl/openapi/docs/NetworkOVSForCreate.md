# NetworkOVSForCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Default** | **bool** |  | 
**Name** | **string** |  | 
**VlanId** | Pointer to **int32** |  | [optional] 

## Methods

### NewNetworkOVSForCreate

`func NewNetworkOVSForCreate(default_ bool, name string, ) *NetworkOVSForCreate`

NewNetworkOVSForCreate instantiates a new NetworkOVSForCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkOVSForCreateWithDefaults

`func NewNetworkOVSForCreateWithDefaults() *NetworkOVSForCreate`

NewNetworkOVSForCreateWithDefaults instantiates a new NetworkOVSForCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDefault

`func (o *NetworkOVSForCreate) GetDefault() bool`

GetDefault returns the Default field if non-nil, zero value otherwise.

### GetDefaultOk

`func (o *NetworkOVSForCreate) GetDefaultOk() (*bool, bool)`

GetDefaultOk returns a tuple with the Default field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDefault

`func (o *NetworkOVSForCreate) SetDefault(v bool)`

SetDefault sets Default field to given value.


### GetName

`func (o *NetworkOVSForCreate) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *NetworkOVSForCreate) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *NetworkOVSForCreate) SetName(v string)`

SetName sets Name field to given value.


### GetVlanId

`func (o *NetworkOVSForCreate) GetVlanId() int32`

GetVlanId returns the VlanId field if non-nil, zero value otherwise.

### GetVlanIdOk

`func (o *NetworkOVSForCreate) GetVlanIdOk() (*int32, bool)`

GetVlanIdOk returns a tuple with the VlanId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVlanId

`func (o *NetworkOVSForCreate) SetVlanId(v int32)`

SetVlanId sets VlanId field to given value.

### HasVlanId

`func (o *NetworkOVSForCreate) HasVlanId() bool`

HasVlanId returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


