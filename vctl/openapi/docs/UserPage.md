# UserPage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Username** | **string** |  | 
**Scopes** | [**[]UserScope**](UserScope.md) |  | 
**Projects** | [**[]UserProject**](UserProject.md) |  | 

## Methods

### NewUserPage

`func NewUserPage(username string, scopes []UserScope, projects []UserProject, ) *UserPage`

NewUserPage instantiates a new UserPage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewUserPageWithDefaults

`func NewUserPageWithDefaults() *UserPage`

NewUserPageWithDefaults instantiates a new UserPage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetUsername

`func (o *UserPage) GetUsername() string`

GetUsername returns the Username field if non-nil, zero value otherwise.

### GetUsernameOk

`func (o *UserPage) GetUsernameOk() (*string, bool)`

GetUsernameOk returns a tuple with the Username field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsername

`func (o *UserPage) SetUsername(v string)`

SetUsername sets Username field to given value.


### GetScopes

`func (o *UserPage) GetScopes() []UserScope`

GetScopes returns the Scopes field if non-nil, zero value otherwise.

### GetScopesOk

`func (o *UserPage) GetScopesOk() (*[]UserScope, bool)`

GetScopesOk returns a tuple with the Scopes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScopes

`func (o *UserPage) SetScopes(v []UserScope)`

SetScopes sets Scopes field to given value.


### GetProjects

`func (o *UserPage) GetProjects() []UserProject`

GetProjects returns the Projects field if non-nil, zero value otherwise.

### GetProjectsOk

`func (o *UserPage) GetProjectsOk() (*[]UserProject, bool)`

GetProjectsOk returns a tuple with the Projects field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProjects

`func (o *UserPage) SetProjects(v []UserProject)`

SetProjects sets Projects field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


