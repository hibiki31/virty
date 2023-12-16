# DomainForCreateInterface


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**mac** | **str** |  | [optional] 
**network_uuid** | **str** |  | 
**port** | **str** |  | [optional] 

## Example

```python
from virty_client.models.domain_for_create_interface import DomainForCreateInterface

# TODO update the JSON string below
json = "{}"
# create an instance of DomainForCreateInterface from a JSON string
domain_for_create_interface_instance = DomainForCreateInterface.from_json(json)
# print the JSON string representation of the object
print DomainForCreateInterface.to_json()

# convert the object into a dict
domain_for_create_interface_dict = domain_for_create_interface_instance.to_dict()
# create an instance of DomainForCreateInterface from a dict
domain_for_create_interface_form_dict = domain_for_create_interface.from_dict(domain_for_create_interface_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


