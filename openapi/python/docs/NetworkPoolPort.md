# NetworkPoolPort


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**vlan_id** | **int** |  | [optional] 
**network** | [**NetworkForNetworkPool**](NetworkForNetworkPool.md) |  | 

## Example

```python
from virty_client.models.network_pool_port import NetworkPoolPort

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkPoolPort from a JSON string
network_pool_port_instance = NetworkPoolPort.from_json(json)
# print the JSON string representation of the object
print NetworkPoolPort.to_json()

# convert the object into a dict
network_pool_port_dict = network_pool_port_instance.to_dict()
# create an instance of NetworkPoolPort from a dict
network_pool_port_form_dict = network_pool_port.from_dict(network_pool_port_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


