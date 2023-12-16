# StorageContainerForStoragePool


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**storage** | [**StorageForStorageContainer**](StorageForStorageContainer.md) |  | 

## Example

```python
from virty_client.models.storage_container_for_storage_pool import StorageContainerForStoragePool

# TODO update the JSON string below
json = "{}"
# create an instance of StorageContainerForStoragePool from a JSON string
storage_container_for_storage_pool_instance = StorageContainerForStoragePool.from_json(json)
# print the JSON string representation of the object
print StorageContainerForStoragePool.to_json()

# convert the object into a dict
storage_container_for_storage_pool_dict = storage_container_for_storage_pool_instance.to_dict()
# create an instance of StorageContainerForStoragePool from a dict
storage_container_for_storage_pool_form_dict = storage_container_for_storage_pool.from_dict(storage_container_for_storage_pool_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


