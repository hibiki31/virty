# TokenData

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **string** |  | [optional] 
**Scopes** | Pointer to **[]string** |  | [optional] [default to []]
**Role** | Pointer to **[]string** |  | [optional] [default to []]

## Methods

### NewTokenData

`func NewTokenData() *TokenData`

NewTokenData instantiates a new TokenData object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewTokenDataWithDefaults

`func NewTokenDataWithDefaults() *TokenData`

NewTokenDataWithDefaults instantiates a new TokenData object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *TokenData) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *TokenData) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *TokenData) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *TokenData) HasId() bool`

HasId returns a boolean if a field has been set.

### GetScopes

`func (o *TokenData) GetScopes() []string`

GetScopes returns the Scopes field if non-nil, zero value otherwise.

### GetScopesOk

`func (o *TokenData) GetScopesOk() (*[]string, bool)`

GetScopesOk returns a tuple with the Scopes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScopes

`func (o *TokenData) SetScopes(v []string)`

SetScopes sets Scopes field to given value.

### HasScopes

`func (o *TokenData) HasScopes() bool`

HasScopes returns a boolean if a field has been set.

### GetRole

`func (o *TokenData) GetRole() []string`

GetRole returns the Role field if non-nil, zero value otherwise.

### GetRoleOk

`func (o *TokenData) GetRoleOk() (*[]string, bool)`

GetRoleOk returns a tuple with the Role field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRole

`func (o *TokenData) SetRole(v []string)`

SetRole sets Role field to given value.

### HasRole

`func (o *TokenData) HasRole() bool`

HasRole returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


