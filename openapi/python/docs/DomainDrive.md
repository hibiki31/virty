# DomainDrive


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**source** | **str** |  | [optional] 
**target** | **str** |  | [optional] 

## Example

```python
from virty_client.models.domain_drive import DomainDrive

# TODO update the JSON string below
json = "{}"
# create an instance of DomainDrive from a JSON string
domain_drive_instance = DomainDrive.from_json(json)
# print the JSON string representation of the object
print DomainDrive.to_json()

# convert the object into a dict
domain_drive_dict = domain_drive_instance.to_dict()
# create an instance of DomainDrive from a dict
domain_drive_form_dict = domain_drive.from_dict(domain_drive_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


