# NodeRoleForUpdate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**NodeName** | **string** |  | 
**RoleName** | **string** |  | 
**ExtraJson** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewNodeRoleForUpdate

`func NewNodeRoleForUpdate(nodeName string, roleName string, ) *NodeRoleForUpdate`

NewNodeRoleForUpdate instantiates a new NodeRoleForUpdate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNodeRoleForUpdateWithDefaults

`func NewNodeRoleForUpdateWithDefaults() *NodeRoleForUpdate`

NewNodeRoleForUpdateWithDefaults instantiates a new NodeRoleForUpdate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetNodeName

`func (o *NodeRoleForUpdate) GetNodeName() string`

GetNodeName returns the NodeName field if non-nil, zero value otherwise.

### GetNodeNameOk

`func (o *NodeRoleForUpdate) GetNodeNameOk() (*string, bool)`

GetNodeNameOk returns a tuple with the NodeName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNodeName

`func (o *NodeRoleForUpdate) SetNodeName(v string)`

SetNodeName sets NodeName field to given value.


### GetRoleName

`func (o *NodeRoleForUpdate) GetRoleName() string`

GetRoleName returns the RoleName field if non-nil, zero value otherwise.

### GetRoleNameOk

`func (o *NodeRoleForUpdate) GetRoleNameOk() (*string, bool)`

GetRoleNameOk returns a tuple with the RoleName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRoleName

`func (o *NodeRoleForUpdate) SetRoleName(v string)`

SetRoleName sets RoleName field to given value.


### GetExtraJson

`func (o *NodeRoleForUpdate) GetExtraJson() map[string]interface{}`

GetExtraJson returns the ExtraJson field if non-nil, zero value otherwise.

### GetExtraJsonOk

`func (o *NodeRoleForUpdate) GetExtraJsonOk() (*map[string]interface{}, bool)`

GetExtraJsonOk returns a tuple with the ExtraJson field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExtraJson

`func (o *NodeRoleForUpdate) SetExtraJson(v map[string]interface{})`

SetExtraJson sets ExtraJson field to given value.

### HasExtraJson

`func (o *NodeRoleForUpdate) HasExtraJson() bool`

HasExtraJson returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


