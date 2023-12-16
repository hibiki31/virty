# ImageDomain


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**owner_user_id** | **str** |  | [optional] 
**issuance_id** | **int** |  | [optional] 
**name** | **str** |  | 
**uuid** | **str** |  | 

## Example

```python
from virty_client.models.image_domain import ImageDomain

# TODO update the JSON string below
json = "{}"
# create an instance of ImageDomain from a JSON string
image_domain_instance = ImageDomain.from_json(json)
# print the JSON string representation of the object
print ImageDomain.to_json()

# convert the object into a dict
image_domain_dict = image_domain_instance.to_dict()
# create an instance of ImageDomain from a dict
image_domain_form_dict = image_domain.from_dict(image_domain_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


