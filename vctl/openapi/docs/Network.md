# Network

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**Uuid** | **string** |  | 
**Type** | **string** |  | 
**Dhcp** | Pointer to **bool** |  | [optional] 
**Description** | Pointer to **string** |  | [optional] 
**Active** | Pointer to **bool** |  | [optional] 
**Bridge** | Pointer to **string** |  | [optional] 
**AutoStart** | Pointer to **bool** |  | [optional] 
**Portgroups** | [**[]NetworkPortgroup**](NetworkPortgroup.md) |  | 
**NodeName** | **string** |  | 
**UpdateToken** | Pointer to **string** |  | [optional] 

## Methods

### NewNetwork

`func NewNetwork(name string, uuid string, type_ string, portgroups []NetworkPortgroup, nodeName string, ) *Network`

NewNetwork instantiates a new Network object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkWithDefaults

`func NewNetworkWithDefaults() *Network`

NewNetworkWithDefaults instantiates a new Network object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *Network) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *Network) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *Network) SetName(v string)`

SetName sets Name field to given value.


### GetUuid

`func (o *Network) GetUuid() string`

GetUuid returns the Uuid field if non-nil, zero value otherwise.

### GetUuidOk

`func (o *Network) GetUuidOk() (*string, bool)`

GetUuidOk returns a tuple with the Uuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUuid

`func (o *Network) SetUuid(v string)`

SetUuid sets Uuid field to given value.


### GetType

`func (o *Network) GetType() string`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *Network) GetTypeOk() (*string, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *Network) SetType(v string)`

SetType sets Type field to given value.


### GetDhcp

`func (o *Network) GetDhcp() bool`

GetDhcp returns the Dhcp field if non-nil, zero value otherwise.

### GetDhcpOk

`func (o *Network) GetDhcpOk() (*bool, bool)`

GetDhcpOk returns a tuple with the Dhcp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDhcp

`func (o *Network) SetDhcp(v bool)`

SetDhcp sets Dhcp field to given value.

### HasDhcp

`func (o *Network) HasDhcp() bool`

HasDhcp returns a boolean if a field has been set.

### GetDescription

`func (o *Network) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *Network) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *Network) SetDescription(v string)`

SetDescription sets Description field to given value.

### HasDescription

`func (o *Network) HasDescription() bool`

HasDescription returns a boolean if a field has been set.

### GetActive

`func (o *Network) GetActive() bool`

GetActive returns the Active field if non-nil, zero value otherwise.

### GetActiveOk

`func (o *Network) GetActiveOk() (*bool, bool)`

GetActiveOk returns a tuple with the Active field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActive

`func (o *Network) SetActive(v bool)`

SetActive sets Active field to given value.

### HasActive

`func (o *Network) HasActive() bool`

HasActive returns a boolean if a field has been set.

### GetBridge

`func (o *Network) GetBridge() string`

GetBridge returns the Bridge field if non-nil, zero value otherwise.

### GetBridgeOk

`func (o *Network) GetBridgeOk() (*string, bool)`

GetBridgeOk returns a tuple with the Bridge field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBridge

`func (o *Network) SetBridge(v string)`

SetBridge sets Bridge field to given value.

### HasBridge

`func (o *Network) HasBridge() bool`

HasBridge returns a boolean if a field has been set.

### GetAutoStart

`func (o *Network) GetAutoStart() bool`

GetAutoStart returns the AutoStart field if non-nil, zero value otherwise.

### GetAutoStartOk

`func (o *Network) GetAutoStartOk() (*bool, bool)`

GetAutoStartOk returns a tuple with the AutoStart field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAutoStart

`func (o *Network) SetAutoStart(v bool)`

SetAutoStart sets AutoStart field to given value.

### HasAutoStart

`func (o *Network) HasAutoStart() bool`

HasAutoStart returns a boolean if a field has been set.

### GetPortgroups

`func (o *Network) GetPortgroups() []NetworkPortgroup`

GetPortgroups returns the Portgroups field if non-nil, zero value otherwise.

### GetPortgroupsOk

`func (o *Network) GetPortgroupsOk() (*[]NetworkPortgroup, bool)`

GetPortgroupsOk returns a tuple with the Portgroups field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPortgroups

`func (o *Network) SetPortgroups(v []NetworkPortgroup)`

SetPortgroups sets Portgroups field to given value.


### GetNodeName

`func (o *Network) GetNodeName() string`

GetNodeName returns the NodeName field if non-nil, zero value otherwise.

### GetNodeNameOk

`func (o *Network) GetNodeNameOk() (*string, bool)`

GetNodeNameOk returns a tuple with the NodeName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNodeName

`func (o *Network) SetNodeName(v string)`

SetNodeName sets NodeName field to given value.


### GetUpdateToken

`func (o *Network) GetUpdateToken() string`

GetUpdateToken returns the UpdateToken field if non-nil, zero value otherwise.

### GetUpdateTokenOk

`func (o *Network) GetUpdateTokenOk() (*string, bool)`

GetUpdateTokenOk returns a tuple with the UpdateToken field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUpdateToken

`func (o *Network) SetUpdateToken(v string)`

SetUpdateToken sets UpdateToken field to given value.

### HasUpdateToken

`func (o *Network) HasUpdateToken() bool`

HasUpdateToken returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


