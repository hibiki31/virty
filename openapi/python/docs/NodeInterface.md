# NodeInterface


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ifname** | **str** |  | 
**operstate** | **str** |  | 
**mtu** | **int** |  | 
**master** | **str** |  | [optional] 
**link_type** | **str** |  | 
**mac_address** | **str** |  | [optional] 
**ipv4_info** | [**List[NodeInterfaceIpv4Info]**](NodeInterfaceIpv4Info.md) |  | 
**ipv6_info** | [**List[NodeInterfaceIpv6Info]**](NodeInterfaceIpv6Info.md) |  | 

## Example

```python
from virty_client.models.node_interface import NodeInterface

# TODO update the JSON string below
json = "{}"
# create an instance of NodeInterface from a JSON string
node_interface_instance = NodeInterface.from_json(json)
# print the JSON string representation of the object
print NodeInterface.to_json()

# convert the object into a dict
node_interface_dict = node_interface_instance.to_dict()
# create an instance of NodeInterface from a dict
node_interface_form_dict = node_interface.from_dict(node_interface_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


