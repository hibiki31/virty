# Flavor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**data** | [**List[FlavorPage]**](FlavorPage.md) |  | 

## Example

```python
from virty_client.models.flavor import Flavor

# TODO update the JSON string below
json = "{}"
# create an instance of Flavor from a JSON string
flavor_instance = Flavor.from_json(json)
# print the JSON string representation of the object
print Flavor.to_json()

# convert the object into a dict
flavor_dict = flavor_instance.to_dict()
# create an instance of Flavor from a dict
flavor_form_dict = flavor.from_dict(flavor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


