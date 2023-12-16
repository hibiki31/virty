# NetworkPoolPort

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | Pointer to **string** |  | [optional] 
**VlanId** | Pointer to **int32** |  | [optional] 
**Network** | [**NetworkForNetworkPool**](NetworkForNetworkPool.md) |  | 

## Methods

### NewNetworkPoolPort

`func NewNetworkPoolPort(network NetworkForNetworkPool, ) *NetworkPoolPort`

NewNetworkPoolPort instantiates a new NetworkPoolPort object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkPoolPortWithDefaults

`func NewNetworkPoolPortWithDefaults() *NetworkPoolPort`

NewNetworkPoolPortWithDefaults instantiates a new NetworkPoolPort object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *NetworkPoolPort) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *NetworkPoolPort) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *NetworkPoolPort) SetName(v string)`

SetName sets Name field to given value.

### HasName

`func (o *NetworkPoolPort) HasName() bool`

HasName returns a boolean if a field has been set.

### GetVlanId

`func (o *NetworkPoolPort) GetVlanId() int32`

GetVlanId returns the VlanId field if non-nil, zero value otherwise.

### GetVlanIdOk

`func (o *NetworkPoolPort) GetVlanIdOk() (*int32, bool)`

GetVlanIdOk returns a tuple with the VlanId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVlanId

`func (o *NetworkPoolPort) SetVlanId(v int32)`

SetVlanId sets VlanId field to given value.

### HasVlanId

`func (o *NetworkPoolPort) HasVlanId() bool`

HasVlanId returns a boolean if a field has been set.

### GetNetwork

`func (o *NetworkPoolPort) GetNetwork() NetworkForNetworkPool`

GetNetwork returns the Network field if non-nil, zero value otherwise.

### GetNetworkOk

`func (o *NetworkPoolPort) GetNetworkOk() (*NetworkForNetworkPool, bool)`

GetNetworkOk returns a tuple with the Network field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNetwork

`func (o *NetworkPoolPort) SetNetwork(v NetworkForNetworkPool)`

SetNetwork sets Network field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


