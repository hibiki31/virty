# NodeRole


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_name** | **str** |  | 
**extra_json** | **object** |  | [optional] 

## Example

```python
from virty_client.models.node_role import NodeRole

# TODO update the JSON string below
json = "{}"
# create an instance of NodeRole from a JSON string
node_role_instance = NodeRole.from_json(json)
# print the JSON string representation of the object
print NodeRole.to_json()

# convert the object into a dict
node_role_dict = node_role_instance.to_dict()
# create an instance of NodeRole from a dict
node_role_form_dict = node_role.from_dict(node_role_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


