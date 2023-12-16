# NodeRoleForUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node_name** | **str** |  | 
**role_name** | **str** |  | 
**extra_json** | **object** |  | [optional] 

## Example

```python
from virty_client.models.node_role_for_update import NodeRoleForUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of NodeRoleForUpdate from a JSON string
node_role_for_update_instance = NodeRoleForUpdate.from_json(json)
# print the JSON string representation of the object
print NodeRoleForUpdate.to_json()

# convert the object into a dict
node_role_for_update_dict = node_role_for_update_instance.to_dict()
# create an instance of NodeRoleForUpdate from a dict
node_role_for_update_form_dict = node_role_for_update.from_dict(node_role_for_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


