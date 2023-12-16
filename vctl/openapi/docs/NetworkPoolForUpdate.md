# NetworkPoolForUpdate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**PoolId** | **int32** |  | 
**NetworkUuid** | **string** |  | 
**PortName** | Pointer to **string** |  | [optional] 

## Methods

### NewNetworkPoolForUpdate

`func NewNetworkPoolForUpdate(poolId int32, networkUuid string, ) *NetworkPoolForUpdate`

NewNetworkPoolForUpdate instantiates a new NetworkPoolForUpdate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkPoolForUpdateWithDefaults

`func NewNetworkPoolForUpdateWithDefaults() *NetworkPoolForUpdate`

NewNetworkPoolForUpdateWithDefaults instantiates a new NetworkPoolForUpdate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPoolId

`func (o *NetworkPoolForUpdate) GetPoolId() int32`

GetPoolId returns the PoolId field if non-nil, zero value otherwise.

### GetPoolIdOk

`func (o *NetworkPoolForUpdate) GetPoolIdOk() (*int32, bool)`

GetPoolIdOk returns a tuple with the PoolId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPoolId

`func (o *NetworkPoolForUpdate) SetPoolId(v int32)`

SetPoolId sets PoolId field to given value.


### GetNetworkUuid

`func (o *NetworkPoolForUpdate) GetNetworkUuid() string`

GetNetworkUuid returns the NetworkUuid field if non-nil, zero value otherwise.

### GetNetworkUuidOk

`func (o *NetworkPoolForUpdate) GetNetworkUuidOk() (*string, bool)`

GetNetworkUuidOk returns a tuple with the NetworkUuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNetworkUuid

`func (o *NetworkPoolForUpdate) SetNetworkUuid(v string)`

SetNetworkUuid sets NetworkUuid field to given value.


### GetPortName

`func (o *NetworkPoolForUpdate) GetPortName() string`

GetPortName returns the PortName field if non-nil, zero value otherwise.

### GetPortNameOk

`func (o *NetworkPoolForUpdate) GetPortNameOk() (*string, bool)`

GetPortNameOk returns a tuple with the PortName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPortName

`func (o *NetworkPoolForUpdate) SetPortName(v string)`

SetPortName sets PortName field to given value.

### HasPortName

`func (o *NetworkPoolForUpdate) HasPortName() bool`

HasPortName returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


