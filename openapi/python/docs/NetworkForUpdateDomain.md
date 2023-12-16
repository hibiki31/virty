# NetworkForUpdateDomain


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mac** | **str** |  | 
**network_uuid** | **str** |  | 
**port** | **str** |  | [optional] 

## Example

```python
from virty_client.models.network_for_update_domain import NetworkForUpdateDomain

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkForUpdateDomain from a JSON string
network_for_update_domain_instance = NetworkForUpdateDomain.from_json(json)
# print the JSON string representation of the object
print NetworkForUpdateDomain.to_json()

# convert the object into a dict
network_for_update_domain_dict = network_for_update_domain_instance.to_dict()
# create an instance of NetworkForUpdateDomain from a dict
network_for_update_domain_form_dict = network_for_update_domain.from_dict(network_for_update_domain_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


