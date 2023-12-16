# CloudInitInsert


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hostname** | **str** |  | 
**user_data** | **str** |  | 

## Example

```python
from virty_client.models.cloud_init_insert import CloudInitInsert

# TODO update the JSON string below
json = "{}"
# create an instance of CloudInitInsert from a JSON string
cloud_init_insert_instance = CloudInitInsert.from_json(json)
# print the JSON string representation of the object
print CloudInitInsert.to_json()

# convert the object into a dict
cloud_init_insert_dict = cloud_init_insert_instance.to_dict()
# create an instance of CloudInitInsert from a dict
cloud_init_insert_form_dict = cloud_init_insert.from_dict(cloud_init_insert_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


