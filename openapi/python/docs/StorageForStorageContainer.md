# StorageForStorageContainer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**uuid** | **str** |  | 
**node_name** | **str** |  | 

## Example

```python
from virty_client.models.storage_for_storage_container import StorageForStorageContainer

# TODO update the JSON string below
json = "{}"
# create an instance of StorageForStorageContainer from a JSON string
storage_for_storage_container_instance = StorageForStorageContainer.from_json(json)
# print the JSON string representation of the object
print StorageForStorageContainer.to_json()

# convert the object into a dict
storage_for_storage_container_dict = storage_for_storage_container_instance.to_dict()
# create an instance of StorageForStorageContainer from a dict
storage_for_storage_container_form_dict = storage_for_storage_container.from_dict(storage_for_storage_container_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


