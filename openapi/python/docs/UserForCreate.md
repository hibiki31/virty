# UserForCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** |  | 
**password** | **str** |  | 

## Example

```python
from virty_client.models.user_for_create import UserForCreate

# TODO update the JSON string below
json = "{}"
# create an instance of UserForCreate from a JSON string
user_for_create_instance = UserForCreate.from_json(json)
# print the JSON string representation of the object
print UserForCreate.to_json()

# convert the object into a dict
user_for_create_dict = user_for_create_instance.to_dict()
# create an instance of UserForCreate from a dict
user_for_create_form_dict = user_for_create.from_dict(user_for_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


