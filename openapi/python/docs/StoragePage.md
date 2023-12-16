# StoragePage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**uuid** | **str** |  | 
**status** | **int** |  | 
**active** | **bool** |  | 
**available** | **int** |  | [optional] 
**capacity** | **int** |  | [optional] 
**node_name** | **str** |  | 
**node** | [**NodePage**](NodePage.md) |  | 
**auto_start** | **bool** |  | 
**path** | **str** |  | [optional] 
**meta_data** | [**StorageMetadata**](StorageMetadata.md) |  | [optional] 
**update_token** | **str** |  | [optional] 
**allocation_commit** | **int** |  | [optional] 
**capacity_commit** | **int** |  | [optional] 

## Example

```python
from virty_client.models.storage_page import StoragePage

# TODO update the JSON string below
json = "{}"
# create an instance of StoragePage from a JSON string
storage_page_instance = StoragePage.from_json(json)
# print the JSON string representation of the object
print StoragePage.to_json()

# convert the object into a dict
storage_page_dict = storage_page_instance.to_dict()
# create an instance of StoragePage from a dict
storage_page_form_dict = storage_page.from_dict(storage_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


