# NodeInterfaceIpv6Info


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address** | **str** |  | 
**prefixlen** | **int** |  | 

## Example

```python
from virty_client.models.node_interface_ipv6_info import NodeInterfaceIpv6Info

# TODO update the JSON string below
json = "{}"
# create an instance of NodeInterfaceIpv6Info from a JSON string
node_interface_ipv6_info_instance = NodeInterfaceIpv6Info.from_json(json)
# print the JSON string representation of the object
print NodeInterfaceIpv6Info.to_json()

# convert the object into a dict
node_interface_ipv6_info_dict = node_interface_ipv6_info_instance.to_dict()
# create an instance of NodeInterfaceIpv6Info from a dict
node_interface_ipv6_info_form_dict = node_interface_ipv6_info.from_dict(node_interface_ipv6_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


