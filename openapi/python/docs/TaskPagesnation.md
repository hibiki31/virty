# TaskPagesnation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**data** | [**List[Task]**](Task.md) |  | 

## Example

```python
from virty_client.models.task_pagesnation import TaskPagesnation

# TODO update the JSON string below
json = "{}"
# create an instance of TaskPagesnation from a JSON string
task_pagesnation_instance = TaskPagesnation.from_json(json)
# print the JSON string representation of the object
print TaskPagesnation.to_json()

# convert the object into a dict
task_pagesnation_dict = task_pagesnation_instance.to_dict()
# create an instance of TaskPagesnation from a dict
task_pagesnation_form_dict = task_pagesnation.from_dict(task_pagesnation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


