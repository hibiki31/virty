# SetupRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** |  | 
**password** | **str** |  | 

## Example

```python
from virty_client.models.setup_request import SetupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SetupRequest from a JSON string
setup_request_instance = SetupRequest.from_json(json)
# print the JSON string representation of the object
print SetupRequest.to_json()

# convert the object into a dict
setup_request_dict = setup_request_instance.to_dict()
# create an instance of SetupRequest from a dict
setup_request_form_dict = setup_request.from_dict(setup_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


