# CloudInitInsert

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Hostname** | **string** |  | 
**UserData** | **string** |  | 

## Methods

### NewCloudInitInsert

`func NewCloudInitInsert(hostname string, userData string, ) *CloudInitInsert`

NewCloudInitInsert instantiates a new CloudInitInsert object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCloudInitInsertWithDefaults

`func NewCloudInitInsertWithDefaults() *CloudInitInsert`

NewCloudInitInsertWithDefaults instantiates a new CloudInitInsert object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetHostname

`func (o *CloudInitInsert) GetHostname() string`

GetHostname returns the Hostname field if non-nil, zero value otherwise.

### GetHostnameOk

`func (o *CloudInitInsert) GetHostnameOk() (*string, bool)`

GetHostnameOk returns a tuple with the Hostname field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHostname

`func (o *CloudInitInsert) SetHostname(v string)`

SetHostname sets Hostname field to given value.


### GetUserData

`func (o *CloudInitInsert) GetUserData() string`

GetUserData returns the UserData field if non-nil, zero value otherwise.

### GetUserDataOk

`func (o *CloudInitInsert) GetUserDataOk() (*string, bool)`

GetUserDataOk returns a tuple with the UserData field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserData

`func (o *CloudInitInsert) SetUserData(v string)`

SetUserData sets UserData field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


