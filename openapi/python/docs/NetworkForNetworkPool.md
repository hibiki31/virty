# NetworkForNetworkPool


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**uuid** | **str** |  | 
**node_name** | **str** |  | 
**bridge** | **str** |  | 
**type** | **str** |  | 

## Example

```python
from virty_client.models.network_for_network_pool import NetworkForNetworkPool

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkForNetworkPool from a JSON string
network_for_network_pool_instance = NetworkForNetworkPool.from_json(json)
# print the JSON string representation of the object
print NetworkForNetworkPool.to_json()

# convert the object into a dict
network_for_network_pool_dict = network_for_network_pool_instance.to_dict()
# create an instance of NetworkForNetworkPool from a dict
network_for_network_pool_form_dict = network_for_network_pool.from_dict(network_for_network_pool_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


