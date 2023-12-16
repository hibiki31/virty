# UserPage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** |  | 
**scopes** | [**List[UserScope]**](UserScope.md) |  | 
**projects** | [**List[UserProject]**](UserProject.md) |  | 

## Example

```python
from virty_client.models.user_page import UserPage

# TODO update the JSON string below
json = "{}"
# create an instance of UserPage from a JSON string
user_page_instance = UserPage.from_json(json)
# print the JSON string representation of the object
print UserPage.to_json()

# convert the object into a dict
user_page_dict = user_page_instance.to_dict()
# create an instance of UserPage from a dict
user_page_form_dict = user_page.from_dict(user_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


