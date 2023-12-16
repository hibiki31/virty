# NetworkPool

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**Name** | Pointer to **string** |  | [optional] 
**Networks** | Pointer to [**[]NetworkForNetworkPool**](NetworkForNetworkPool.md) |  | [optional] 
**Ports** | Pointer to [**[]NetworkPoolPort**](NetworkPoolPort.md) |  | [optional] 

## Methods

### NewNetworkPool

`func NewNetworkPool() *NetworkPool`

NewNetworkPool instantiates a new NetworkPool object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkPoolWithDefaults

`func NewNetworkPoolWithDefaults() *NetworkPool`

NewNetworkPoolWithDefaults instantiates a new NetworkPool object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *NetworkPool) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *NetworkPool) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *NetworkPool) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *NetworkPool) HasId() bool`

HasId returns a boolean if a field has been set.

### GetName

`func (o *NetworkPool) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *NetworkPool) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *NetworkPool) SetName(v string)`

SetName sets Name field to given value.

### HasName

`func (o *NetworkPool) HasName() bool`

HasName returns a boolean if a field has been set.

### GetNetworks

`func (o *NetworkPool) GetNetworks() []NetworkForNetworkPool`

GetNetworks returns the Networks field if non-nil, zero value otherwise.

### GetNetworksOk

`func (o *NetworkPool) GetNetworksOk() (*[]NetworkForNetworkPool, bool)`

GetNetworksOk returns a tuple with the Networks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNetworks

`func (o *NetworkPool) SetNetworks(v []NetworkForNetworkPool)`

SetNetworks sets Networks field to given value.

### HasNetworks

`func (o *NetworkPool) HasNetworks() bool`

HasNetworks returns a boolean if a field has been set.

### GetPorts

`func (o *NetworkPool) GetPorts() []NetworkPoolPort`

GetPorts returns the Ports field if non-nil, zero value otherwise.

### GetPortsOk

`func (o *NetworkPool) GetPortsOk() (*[]NetworkPoolPort, bool)`

GetPortsOk returns a tuple with the Ports field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPorts

`func (o *NetworkPool) SetPorts(v []NetworkPoolPort)`

SetPorts sets Ports field to given value.

### HasPorts

`func (o *NetworkPool) HasPorts() bool`

HasPorts returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


