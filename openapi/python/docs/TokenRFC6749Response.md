# TokenRFC6749Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_token** | **str** |  | 
**token_type** | **str** |  | 

## Example

```python
from virty_client.models.token_rfc6749_response import TokenRFC6749Response

# TODO update the JSON string below
json = "{}"
# create an instance of TokenRFC6749Response from a JSON string
token_rfc6749_response_instance = TokenRFC6749Response.from_json(json)
# print the JSON string representation of the object
print TokenRFC6749Response.to_json()

# convert the object into a dict
token_rfc6749_response_dict = token_rfc6749_response_instance.to_dict()
# create an instance of TokenRFC6749Response from a dict
token_rfc6749_response_form_dict = token_rfc6749_response.from_dict(token_rfc6749_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


