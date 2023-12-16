# NodeForCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**Description** | **string** |  | 
**Domain** | **string** |  | 
**UserName** | **string** |  | 
**Port** | **int32** |  | 
**LibvirtRole** | **bool** |  | 

## Methods

### NewNodeForCreate

`func NewNodeForCreate(name string, description string, domain string, userName string, port int32, libvirtRole bool, ) *NodeForCreate`

NewNodeForCreate instantiates a new NodeForCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNodeForCreateWithDefaults

`func NewNodeForCreateWithDefaults() *NodeForCreate`

NewNodeForCreateWithDefaults instantiates a new NodeForCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *NodeForCreate) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *NodeForCreate) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *NodeForCreate) SetName(v string)`

SetName sets Name field to given value.


### GetDescription

`func (o *NodeForCreate) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *NodeForCreate) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *NodeForCreate) SetDescription(v string)`

SetDescription sets Description field to given value.


### GetDomain

`func (o *NodeForCreate) GetDomain() string`

GetDomain returns the Domain field if non-nil, zero value otherwise.

### GetDomainOk

`func (o *NodeForCreate) GetDomainOk() (*string, bool)`

GetDomainOk returns a tuple with the Domain field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDomain

`func (o *NodeForCreate) SetDomain(v string)`

SetDomain sets Domain field to given value.


### GetUserName

`func (o *NodeForCreate) GetUserName() string`

GetUserName returns the UserName field if non-nil, zero value otherwise.

### GetUserNameOk

`func (o *NodeForCreate) GetUserNameOk() (*string, bool)`

GetUserNameOk returns a tuple with the UserName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserName

`func (o *NodeForCreate) SetUserName(v string)`

SetUserName sets UserName field to given value.


### GetPort

`func (o *NodeForCreate) GetPort() int32`

GetPort returns the Port field if non-nil, zero value otherwise.

### GetPortOk

`func (o *NodeForCreate) GetPortOk() (*int32, bool)`

GetPortOk returns a tuple with the Port field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPort

`func (o *NodeForCreate) SetPort(v int32)`

SetPort sets Port field to given value.


### GetLibvirtRole

`func (o *NodeForCreate) GetLibvirtRole() bool`

GetLibvirtRole returns the LibvirtRole field if non-nil, zero value otherwise.

### GetLibvirtRoleOk

`func (o *NodeForCreate) GetLibvirtRoleOk() (*bool, bool)`

GetLibvirtRoleOk returns a tuple with the LibvirtRole field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLibvirtRole

`func (o *NodeForCreate) SetLibvirtRole(v bool)`

SetLibvirtRole sets LibvirtRole field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


