# ImageDownloadForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**storage_uuid** | **str** |  | 
**image_url** | **str** |  | 

## Example

```python
from virty_client.models.image_download_for_create import ImageDownloadForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ImageDownloadForCreate from a JSON string
image_download_for_create_instance = ImageDownloadForCreate.from_json(json)
# print the JSON string representation of the object
print ImageDownloadForCreate.to_json()

# convert the object into a dict
image_download_for_create_dict = image_download_for_create_instance.to_dict()
# create an instance of ImageDownloadForCreate from a dict
image_download_for_create_form_dict = image_download_for_create.from_dict(image_download_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


