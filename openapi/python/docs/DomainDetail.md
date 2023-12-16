# DomainDetail


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
**node** | [**Node**](Node.md) |  | 

## Example

```python
from virty_client.models.domain_detail import DomainDetail

# TODO update the JSON string below
json = "{}"
# create an instance of DomainDetail from a JSON string
domain_detail_instance = DomainDetail.from_json(json)
# print the JSON string representation of the object
print DomainDetail.to_json()

# convert the object into a dict
domain_detail_dict = domain_detail_instance.to_dict()
# create an instance of DomainDetail from a dict
domain_detail_form_dict = domain_detail.from_dict(domain_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


