# NetworkPage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**data** | [**List[Network]**](Network.md) |  | 

## Example

```python
from virty_client.models.network_page import NetworkPage

# TODO update the JSON string below
json = "{}"
# create an instance of NetworkPage from a JSON string
network_page_instance = NetworkPage.from_json(json)
# print the JSON string representation of the object
print NetworkPage.to_json()

# convert the object into a dict
network_page_dict = network_page_instance.to_dict()
# create an instance of NetworkPage from a dict
network_page_form_dict = network_page.from_dict(network_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


