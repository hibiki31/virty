# NetworkPortgroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**vlan_id** | **str** |  | [optional] 
**is_default** | **bool** |  | 

## Example

```python
from virty_client.models.network_portgroup import NetworkPortgroup

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkPortgroup from a JSON string
network_portgroup_instance = NetworkPortgroup.from_json(json)
# print the JSON string representation of the object
print NetworkPortgroup.to_json()

# convert the object into a dict
network_portgroup_dict = network_portgroup_instance.to_dict()
# create an instance of NetworkPortgroup from a dict
network_portgroup_form_dict = network_portgroup.from_dict(network_portgroup_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


