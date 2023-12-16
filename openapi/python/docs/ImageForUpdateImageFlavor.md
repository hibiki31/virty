# ImageForUpdateImageFlavor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**storage_uuid** | **str** |  | 
**path** | **str** |  | 
**node_name** | **str** |  | 
**flavor_id** | **int** |  | 

## Example

```python
from virty_client.models.image_for_update_image_flavor import ImageForUpdateImageFlavor

# TODO update the JSON string below
json = "{}"
# create an instance of ImageForUpdateImageFlavor from a JSON string
image_for_update_image_flavor_instance = ImageForUpdateImageFlavor.from_json(json)
# print the JSON string representation of the object
print ImageForUpdateImageFlavor.to_json()

# convert the object into a dict
image_for_update_image_flavor_dict = image_for_update_image_flavor_instance.to_dict()
# create an instance of ImageForUpdateImageFlavor from a dict
image_for_update_image_flavor_form_dict = image_for_update_image_flavor.from_dict(image_for_update_image_flavor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


