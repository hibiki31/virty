# SSHKeyPair


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**private_key** | **str** |  | 
**public_key** | **str** |  | 

## Example

```python
from virty_client.models.ssh_key_pair import SSHKeyPair

# TODO update the JSON string below
json = "{}"
# create an instance of SSHKeyPair from a JSON string
ssh_key_pair_instance = SSHKeyPair.from_json(json)
# print the JSON string representation of the object
print SSHKeyPair.to_json()

# convert the object into a dict
ssh_key_pair_dict = ssh_key_pair_instance.to_dict()
# create an instance of SSHKeyPair from a dict
ssh_key_pair_form_dict = ssh_key_pair.from_dict(ssh_key_pair_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


