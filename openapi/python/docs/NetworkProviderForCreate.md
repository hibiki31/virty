# NetworkProviderForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**dns_domain** | **str** |  | [optional] 
**network_address** | **str** |  | [optional] 
**network_prefix** | **str** |  | [optional] 
**gateway_address** | **str** |  | [optional] 
**dhcp_start** | **str** |  | [optional] 
**dhcp_end** | **str** |  | [optional] 
**network_node** | **str** |  | [optional] 

## Example

```python
from virty_client.models.network_provider_for_create import NetworkProviderForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkProviderForCreate from a JSON string
network_provider_for_create_instance = NetworkProviderForCreate.from_json(json)
# print the JSON string representation of the object
print NetworkProviderForCreate.to_json()

# convert the object into a dict
network_provider_for_create_dict = network_provider_for_create_instance.to_dict()
# create an instance of NetworkProviderForCreate from a dict
network_provider_for_create_form_dict = network_provider_for_create.from_dict(network_provider_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


