# NetworkForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**node_name** | **str** |  | 
**type** | **str** | brdige or ovs | 
**bridge_device** | **str** |  | [optional] 

## Example

```python
from virty_client.models.network_for_create import NetworkForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkForCreate from a JSON string
network_for_create_instance = NetworkForCreate.from_json(json)
# print the JSON string representation of the object
print NetworkForCreate.to_json()

# convert the object into a dict
network_for_create_dict = network_for_create_instance.to_dict()
# create an instance of NetworkForCreate from a dict
network_for_create_form_dict = network_for_create.from_dict(network_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


