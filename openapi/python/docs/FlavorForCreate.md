# FlavorForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**os** | **str** |  | 
**manual_url** | **str** |  | 
**icon** | **str** |  | 
**cloud_init_ready** | **bool** |  | 
**description** | **str** |  | 

## Example

```python
from virty_client.models.flavor_for_create import FlavorForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of FlavorForCreate from a JSON string
flavor_for_create_instance = FlavorForCreate.from_json(json)
# print the JSON string representation of the object
print FlavorForCreate.to_json()

# convert the object into a dict
flavor_for_create_dict = flavor_for_create_instance.to_dict()
# create an instance of FlavorForCreate from a dict
flavor_for_create_form_dict = flavor_for_create.from_dict(flavor_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


