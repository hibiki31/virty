# StoragePoolForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**storage_uuids** | **List[str]** |  | 

## Example

```python
from virty_client.models.storage_pool_for_create import StoragePoolForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of StoragePoolForCreate from a JSON string
storage_pool_for_create_instance = StoragePoolForCreate.from_json(json)
# print the JSON string representation of the object
print StoragePoolForCreate.to_json()

# convert the object into a dict
storage_pool_for_create_dict = storage_pool_for_create_instance.to_dict()
# create an instance of StoragePoolForCreate from a dict
storage_pool_for_create_form_dict = storage_pool_for_create.from_dict(storage_pool_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


