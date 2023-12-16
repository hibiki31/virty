# StorageMetadataForUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** |  | 
**rool** | **str** |  | 
**protocol** | **str** |  | 
**device_type** | **str** |  | 

## Example

```python
from virty_client.models.storage_metadata_for_update import StorageMetadataForUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of StorageMetadataForUpdate from a JSON string
storage_metadata_for_update_instance = StorageMetadataForUpdate.from_json(json)
# print the JSON string representation of the object
print StorageMetadataForUpdate.to_json()

# convert the object into a dict
storage_metadata_for_update_dict = storage_metadata_for_update_instance.to_dict()
# create an instance of StorageMetadataForUpdate from a dict
storage_metadata_for_update_form_dict = storage_metadata_for_update.from_dict(storage_metadata_for_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


