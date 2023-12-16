# NetworkPoolForUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pool_id** | **int** |  | 
**network_uuid** | **str** |  | 
**port_name** | **str** |  | [optional] 

## Example

```python
from virty_client.models.network_pool_for_update import NetworkPoolForUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkPoolForUpdate from a JSON string
network_pool_for_update_instance = NetworkPoolForUpdate.from_json(json)
# print the JSON string representation of the object
print NetworkPoolForUpdate.to_json()

# convert the object into a dict
network_pool_for_update_dict = network_pool_for_update_instance.to_dict()
# create an instance of NetworkPoolForUpdate from a dict
network_pool_for_update_form_dict = network_pool_for_update.from_dict(network_pool_for_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


