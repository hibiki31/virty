# DomainForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**name** | **str** |  | 
**node_name** | **str** |  | 
**memory_mega_byte** | **int** |  | 
**cpu** | **int** |  | 
**disks** | [**List[DomainForCreateDisk]**](DomainForCreateDisk.md) |  | 
**interface** | [**List[DomainForCreateInterface]**](DomainForCreateInterface.md) |  | 
**cloud_init** | [**CloudInitInsert**](CloudInitInsert.md) |  | [optional] 

## Example

```python
from virty_client.models.domain_for_create import DomainForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of DomainForCreate from a JSON string
domain_for_create_instance = DomainForCreate.from_json(json)
# print the JSON string representation of the object
print DomainForCreate.to_json()

# convert the object into a dict
domain_for_create_dict = domain_for_create_instance.to_dict()
# create an instance of DomainForCreate from a dict
domain_for_create_form_dict = domain_for_create.from_dict(domain_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


