# DomainInterface


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**mac** | **str** |  | [optional] 
**target** | **str** |  | [optional] 
**bridge** | **str** |  | [optional] 
**network** | **str** |  | [optional] 
**port** | **str** |  | [optional] 

## Example

```python
from virty_client.models.domain_interface import DomainInterface

# TODO update the JSON string below
json = "{}"
# create an instance of DomainInterface from a JSON string
domain_interface_instance = DomainInterface.from_json(json)
# print the JSON string representation of the object
print DomainInterface.to_json()

# convert the object into a dict
domain_interface_dict = domain_interface_instance.to_dict()
# create an instance of DomainInterface from a dict
domain_interface_form_dict = domain_interface.from_dict(domain_interface_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


