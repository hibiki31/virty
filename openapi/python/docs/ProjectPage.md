# ProjectPage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**memory_g** | **int** |  | 
**core** | **int** |  | 
**storage_capacity_g** | **int** |  | 
**users** | [**List[ProjectUser]**](ProjectUser.md) |  | 
**used_memory_g** | **int** |  | 
**used_core** | **int** |  | 
**network_pools** | **object** |  | [optional] 
**storage_pools** | **object** |  | [optional] 

## Example

```python
from virty_client.models.project_page import ProjectPage

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPage from a JSON string
project_page_instance = ProjectPage.from_json(json)
# print the JSON string representation of the object
print ProjectPage.to_json()

# convert the object into a dict
project_page_dict = project_page_instance.to_dict()
# create an instance of ProjectPage from a dict
project_page_form_dict = project_page.from_dict(project_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


