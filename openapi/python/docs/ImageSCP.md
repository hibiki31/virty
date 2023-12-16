# ImageSCP


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**from_node_name** | **str** |  | 
**to_node_name** | **str** |  | 
**from_file_path** | **str** |  | 
**to_file_path** | **str** |  | 

## Example

```python
from virty_client.models.image_scp import ImageSCP

# TODO update the JSON string below
json = "{}"
# create an instance of ImageSCP from a JSON string
image_scp_instance = ImageSCP.from_json(json)
# print the JSON string representation of the object
print ImageSCP.to_json()

# convert the object into a dict
image_scp_dict = image_scp_instance.to_dict()
# create an instance of ImageSCP from a dict
image_scp_form_dict = image_scp.from_dict(image_scp_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


