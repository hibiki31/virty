# ImagePage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**storage_uuid** | **str** |  | [optional] 
**capacity** | **int** |  | 
**storage** | [**StoragePage**](StoragePage.md) |  | 
**flavor** | [**Flavor**](Flavor.md) |  | [optional] 
**allocation** | **int** |  | 
**path** | **str** |  | 
**update_token** | **str** |  | [optional] 
**domain** | [**ImageDomain**](ImageDomain.md) |  | [optional] 

## Example

```python
from virty_client.models.image_page import ImagePage

# TODO update the JSON string below
json = "{}"
# create an instance of ImagePage from a JSON string
image_page_instance = ImagePage.from_json(json)
# print the JSON string representation of the object
print ImagePage.to_json()

# convert the object into a dict
image_page_dict = image_page_instance.to_dict()
# create an instance of ImagePage from a dict
image_page_form_dict = image_page.from_dict(image_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


