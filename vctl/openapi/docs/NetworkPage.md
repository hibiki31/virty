# NetworkPage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Count** | **int32** |  | 
**Data** | [**[]Network**](Network.md) |  | 

## Methods

### NewNetworkPage

`func NewNetworkPage(count int32, data []Network, ) *NetworkPage`

NewNetworkPage instantiates a new NetworkPage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkPageWithDefaults

`func NewNetworkPageWithDefaults() *NetworkPage`

NewNetworkPageWithDefaults instantiates a new NetworkPage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCount

`func (o *NetworkPage) GetCount() int32`

GetCount returns the Count field if non-nil, zero value otherwise.

### GetCountOk

`func (o *NetworkPage) GetCountOk() (*int32, bool)`

GetCountOk returns a tuple with the Count field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCount

`func (o *NetworkPage) SetCount(v int32)`

SetCount sets Count field to given value.


### GetData

`func (o *NetworkPage) GetData() []Network`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *NetworkPage) GetDataOk() (*[]Network, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *NetworkPage) SetData(v []Network)`

SetData sets Data field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


