# Flavor

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Count** | **int32** |  | 
**Data** | [**[]FlavorPage**](FlavorPage.md) |  | 

## Methods

### NewFlavor

`func NewFlavor(count int32, data []FlavorPage, ) *Flavor`

NewFlavor instantiates a new Flavor object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFlavorWithDefaults

`func NewFlavorWithDefaults() *Flavor`

NewFlavorWithDefaults instantiates a new Flavor object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCount

`func (o *Flavor) GetCount() int32`

GetCount returns the Count field if non-nil, zero value otherwise.

### GetCountOk

`func (o *Flavor) GetCountOk() (*int32, bool)`

GetCountOk returns a tuple with the Count field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCount

`func (o *Flavor) SetCount(v int32)`

SetCount sets Count field to given value.


### GetData

`func (o *Flavor) GetData() []FlavorPage`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *Flavor) GetDataOk() (*[]FlavorPage, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *Flavor) SetData(v []FlavorPage)`

SetData sets Data field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


