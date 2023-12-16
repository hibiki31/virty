# NodeRole

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RoleName** | **string** |  | 
**ExtraJson** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewNodeRole

`func NewNodeRole(roleName string, ) *NodeRole`

NewNodeRole instantiates a new NodeRole object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNodeRoleWithDefaults

`func NewNodeRoleWithDefaults() *NodeRole`

NewNodeRoleWithDefaults instantiates a new NodeRole object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRoleName

`func (o *NodeRole) GetRoleName() string`

GetRoleName returns the RoleName field if non-nil, zero value otherwise.

### GetRoleNameOk

`func (o *NodeRole) GetRoleNameOk() (*string, bool)`

GetRoleNameOk returns a tuple with the RoleName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRoleName

`func (o *NodeRole) SetRoleName(v string)`

SetRoleName sets RoleName field to given value.


### GetExtraJson

`func (o *NodeRole) GetExtraJson() map[string]interface{}`

GetExtraJson returns the ExtraJson field if non-nil, zero value otherwise.

### GetExtraJsonOk

`func (o *NodeRole) GetExtraJsonOk() (*map[string]interface{}, bool)`

GetExtraJsonOk returns a tuple with the ExtraJson field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExtraJson

`func (o *NodeRole) SetExtraJson(v map[string]interface{})`

SetExtraJson sets ExtraJson field to given value.

### HasExtraJson

`func (o *NodeRole) HasExtraJson() bool`

HasExtraJson returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


