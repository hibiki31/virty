# TaskIncomplete


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hash** | **str** |  | 
**count** | **int** |  | 
**uuids** | **List[str]** |  | 

## Example

```python
from virty_client.models.task_incomplete import TaskIncomplete

# TODO update the JSON string below
json = "{}"
# create an instance of TaskIncomplete from a JSON string
task_incomplete_instance = TaskIncomplete.from_json(json)
# print the JSON string representation of the object
print TaskIncomplete.to_json()

# convert the object into a dict
task_incomplete_dict = task_incomplete_instance.to_dict()
# create an instance of TaskIncomplete from a dict
task_incomplete_form_dict = task_incomplete.from_dict(task_incomplete_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


