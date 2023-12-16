# Task


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**post_time** | **datetime** |  | [optional] 
**run_time** | **float** |  | [optional] 
**start_time** | **datetime** |  | [optional] 
**update_time** | **datetime** |  | [optional] 
**user_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**resource** | **str** |  | [optional] 
**object** | **str** |  | [optional] 
**method** | **str** |  | [optional] 
**dependence_uuid** | **str** |  | [optional] 
**request** | **object** |  | [optional] 
**result** | **object** |  | [optional] 
**message** | **str** |  | [optional] 
**log** | **str** |  | [optional] 
**uuid** | **str** |  | [optional] 

## Example

```python
from virty_client.models.task import Task

# TODO update the JSON string below
json = "{}"
# create an instance of Task from a JSON string
task_instance = Task.from_json(json)
# print the JSON string representation of the object
print Task.to_json()

# convert the object into a dict
task_dict = task_instance.to_dict()
# create an instance of Task from a dict
task_form_dict = task.from_dict(task_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


