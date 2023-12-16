# DomainForCreateDisk


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**save_pool_uuid** | **str** |  | 
**original_pool_uuid** | **str** |  | [optional] 
**original_name** | **str** |  | [optional] 
**size_giga_byte** | **int** |  | [optional] 
**template_name** | **str** |  | [optional] 

## Example

```python
from virty_client.models.domain_for_create_disk import DomainForCreateDisk

# TODO update the JSON string below
json = "{}"
# create an instance of DomainForCreateDisk from a JSON string
domain_for_create_disk_instance = DomainForCreateDisk.from_json(json)
# print the JSON string representation of the object
print DomainForCreateDisk.to_json()

# convert the object into a dict
domain_for_create_disk_dict = domain_for_create_disk_instance.to_dict()
# create an instance of DomainForCreateDisk from a dict
domain_for_create_disk_form_dict = domain_for_create_disk.from_dict(domain_for_create_disk_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


