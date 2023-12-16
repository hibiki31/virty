# NodePage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | 
**domain** | **str** |  | 
**user_name** | **str** |  | 
**port** | **int** |  | 
**core** | **int** |  | 
**memory** | **int** |  | 
**cpu_gen** | **str** |  | 
**os_like** | **str** |  | 
**os_name** | **str** |  | 
**os_version** | **str** |  | 
**status** | **int** |  | 
**qemu_version** | **str** |  | [optional] 
**libvirt_version** | **str** |  | [optional] 
**roles** | [**List[NodeRole]**](NodeRole.md) |  | 

## Example

```python
from virty_client.models.node_page import NodePage

# TODO update the JSON string below
json = "{}"
# create an instance of NodePage from a JSON string
node_page_instance = NodePage.from_json(json)
# print the JSON string representation of the object
print NodePage.to_json()

# convert the object into a dict
node_page_dict = node_page_instance.to_dict()
# create an instance of NodePage from a dict
node_page_form_dict = node_page.from_dict(node_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


