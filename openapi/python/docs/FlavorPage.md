# FlavorPage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**os** | **str** |  | 
**manual_url** | **str** |  | 
**icon** | **str** |  | 
**cloud_init_ready** | **bool** |  | 
**description** | **str** |  | 
**id** | **int** |  | 

## Example

```python
from virty_client.models.flavor_page import FlavorPage

# TODO update the JSON string below
json = "{}"
# create an instance of FlavorPage from a JSON string
flavor_page_instance = FlavorPage.from_json(json)
# print the JSON string representation of the object
print FlavorPage.to_json()

# convert the object into a dict
flavor_page_dict = flavor_page_instance.to_dict()
# create an instance of FlavorPage from a dict
flavor_page_form_dict = flavor_page.from_dict(flavor_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


