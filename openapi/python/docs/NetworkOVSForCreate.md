# NetworkOVSForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default** | **bool** |  | 
**name** | **str** |  | 
**vlan_id** | **int** |  | [optional] 

## Example

```python
from virty_client.models.network_ovs_for_create import NetworkOVSForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkOVSForCreate from a JSON string
network_ovs_for_create_instance = NetworkOVSForCreate.from_json(json)
# print the JSON string representation of the object
print NetworkOVSForCreate.to_json()

# convert the object into a dict
network_ovs_for_create_dict = network_ovs_for_create_instance.to_dict()
# create an instance of NetworkOVSForCreate from a dict
network_ovs_for_create_form_dict = network_ovs_for_create.from_dict(network_ovs_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


