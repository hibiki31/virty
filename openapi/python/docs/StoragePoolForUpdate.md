# StoragePoolForUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**storage_uuids** | **List[str]** |  | 

## Example

```python
from virty_client.models.storage_pool_for_update import StoragePoolForUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of StoragePoolForUpdate from a JSON string
storage_pool_for_update_instance = StoragePoolForUpdate.from_json(json)
# print the JSON string representation of the object
print StoragePoolForUpdate.to_json()

# convert the object into a dict
storage_pool_for_update_dict = storage_pool_for_update_instance.to_dict()
# create an instance of StoragePoolForUpdate from a dict
storage_pool_for_update_form_dict = storage_pool_for_update.from_dict(storage_pool_for_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


