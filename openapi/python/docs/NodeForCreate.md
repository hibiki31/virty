# NodeForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | 
**domain** | **str** |  | 
**user_name** | **str** |  | 
**port** | **int** |  | 
**libvirt_role** | **bool** |  | 

## Example

```python
from virty_client.models.node_for_create import NodeForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of NodeForCreate from a JSON string
node_for_create_instance = NodeForCreate.from_json(json)
# print the JSON string representation of the object
print NodeForCreate.to_json()

# convert the object into a dict
node_for_create_dict = node_for_create_instance.to_dict()
# create an instance of NodeForCreate from a dict
node_for_create_form_dict = node_for_create.from_dict(node_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


