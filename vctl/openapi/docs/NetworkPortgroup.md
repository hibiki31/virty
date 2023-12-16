# NetworkPortgroup

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**VlanId** | Pointer to **string** |  | [optional] 
**IsDefault** | **bool** |  | 

## Methods

### NewNetworkPortgroup

`func NewNetworkPortgroup(name string, isDefault bool, ) *NetworkPortgroup`

NewNetworkPortgroup instantiates a new NetworkPortgroup object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkPortgroupWithDefaults

`func NewNetworkPortgroupWithDefaults() *NetworkPortgroup`

NewNetworkPortgroupWithDefaults instantiates a new NetworkPortgroup object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *NetworkPortgroup) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *NetworkPortgroup) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *NetworkPortgroup) SetName(v string)`

SetName sets Name field to given value.


### GetVlanId

`func (o *NetworkPortgroup) GetVlanId() string`

GetVlanId returns the VlanId field if non-nil, zero value otherwise.

### GetVlanIdOk

`func (o *NetworkPortgroup) GetVlanIdOk() (*string, bool)`

GetVlanIdOk returns a tuple with the VlanId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVlanId

`func (o *NetworkPortgroup) SetVlanId(v string)`

SetVlanId sets VlanId field to given value.

### HasVlanId

`func (o *NetworkPortgroup) HasVlanId() bool`

HasVlanId returns a boolean if a field has been set.

### GetIsDefault

`func (o *NetworkPortgroup) GetIsDefault() bool`

GetIsDefault returns the IsDefault field if non-nil, zero value otherwise.

### GetIsDefaultOk

`func (o *NetworkPortgroup) GetIsDefaultOk() (*bool, bool)`

GetIsDefaultOk returns a tuple with the IsDefault field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsDefault

`func (o *NetworkPortgroup) SetIsDefault(v bool)`

SetIsDefault sets IsDefault field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


