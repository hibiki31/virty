# NodeInterfaceIpv4Info


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address** | **str** |  | 
**prefixlen** | **int** |  | 
**label** | **str** |  | 

## Example

```python
from virty_client.models.node_interface_ipv4_info import NodeInterfaceIpv4Info

# TODO update the JSON string below
json = "{}"
# create an instance of NodeInterfaceIpv4Info from a JSON string
node_interface_ipv4_info_instance = NodeInterfaceIpv4Info.from_json(json)
# print the JSON string representation of the object
print NodeInterfaceIpv4Info.to_json()

# convert the object into a dict
node_interface_ipv4_info_dict = node_interface_ipv4_info_instance.to_dict()
# create an instance of NodeInterfaceIpv4Info from a dict
node_interface_ipv4_info_form_dict = node_interface_ipv4_info.from_dict(node_interface_ipv4_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


