# StorageForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**node_name** | **str** |  | 
**path** | **str** |  | 

## Example

```python
from virty_client.models.storage_for_create import StorageForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of StorageForCreate from a JSON string
storage_for_create_instance = StorageForCreate.from_json(json)
# print the JSON string representation of the object
print StorageForCreate.to_json()

# convert the object into a dict
storage_for_create_dict = storage_for_create_instance.to_dict()
# create an instance of StorageForCreate from a dict
storage_for_create_form_dict = storage_for_create.from_dict(storage_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


