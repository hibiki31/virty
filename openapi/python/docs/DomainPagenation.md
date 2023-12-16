# DomainPagenation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**data** | [**List[Domain]**](Domain.md) |  | 

## Example

```python
from virty_client.models.domain_pagenation import DomainPagenation

# TODO update the JSON string below
json = "{}"
# create an instance of DomainPagenation from a JSON string
domain_pagenation_instance = DomainPagenation.from_json(json)
# print the JSON string representation of the object
print DomainPagenation.to_json()

# convert the object into a dict
domain_pagenation_dict = domain_pagenation_instance.to_dict()
# create an instance of DomainPagenation from a dict
domain_pagenation_form_dict = domain_pagenation.from_dict(domain_pagenation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


