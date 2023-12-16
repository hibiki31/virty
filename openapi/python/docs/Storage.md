# Storage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**data** | [**List[StoragePage]**](StoragePage.md) |  | 

## Example

```python
from virty_client.models.storage import Storage

# TODO update the JSON string below
json = "{}"
# create an instance of Storage from a JSON string
storage_instance = Storage.from_json(json)
# print the JSON string representation of the object
print Storage.to_json()

# convert the object into a dict
storage_dict = storage_instance.to_dict()
# create an instance of Storage from a dict
storage_form_dict = storage.from_dict(storage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


