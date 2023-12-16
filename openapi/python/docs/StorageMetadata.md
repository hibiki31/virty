# StorageMetadata


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rool** | **str** |  | [optional] 
**protocol** | **str** |  | [optional] 
**device_type** | **str** |  | [optional] 

## Example

```python
from virty_client.models.storage_metadata import StorageMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of StorageMetadata from a JSON string
storage_metadata_instance = StorageMetadata.from_json(json)
# print the JSON string representation of the object
print StorageMetadata.to_json()

# convert the object into a dict
storage_metadata_dict = storage_metadata_instance.to_dict()
# create an instance of StorageMetadata from a dict
storage_metadata_form_dict = storage_metadata.from_dict(storage_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


