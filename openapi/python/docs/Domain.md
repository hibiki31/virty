# Domain


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** |  | 
**name** | **str** |  | 
**core** | **int** |  | 
**memory** | **int** |  | 
**status** | **int** |  | 
**description** | **str** |  | [optional] 
**node_name** | **str** |  | 
**owner_user_id** | **str** |  | [optional] 
**owner_project_id** | **str** |  | [optional] 
**owner_project** | [**DomainProject**](DomainProject.md) |  | [optional] 
**vnc_port** | **int** |  | [optional] 
**vnc_password** | **str** |  | [optional] 
**drives** | [**List[DomainDrive]**](DomainDrive.md) |  | [optional] 
**interfaces** | [**List[DomainInterface]**](DomainInterface.md) |  | [optional] 

## Example

```python
from virty_client.models.domain import Domain

# TODO update the JSON string below
json = "{}"
# create an instance of Domain from a JSON string
domain_instance = Domain.from_json(json)
# print the JSON string representation of the object
print Domain.to_json()

# convert the object into a dict
domain_dict = domain_instance.to_dict()
# create an instance of Domain from a dict
domain_form_dict = domain.from_dict(domain_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


