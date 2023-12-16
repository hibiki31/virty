# StoragePool


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**storages** | [**List[StorageContainerForStoragePool]**](StorageContainerForStoragePool.md) |  | 

## Example

```python
from virty_client.models.storage_pool import StoragePool

# TODO update the JSON string below
json = "{}"
# create an instance of StoragePool from a JSON string
storage_pool_instance = StoragePool.from_json(json)
# print the JSON string representation of the object
print StoragePool.to_json()

# convert the object into a dict
storage_pool_dict = storage_pool_instance.to_dict()
# create an instance of StoragePool from a dict
storage_pool_form_dict = storage_pool.from_dict(storage_pool_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


