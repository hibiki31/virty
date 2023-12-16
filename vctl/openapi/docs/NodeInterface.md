# NodeInterface

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Ifname** | **string** |  | 
**Operstate** | **string** |  | 
**Mtu** | **int32** |  | 
**Master** | Pointer to **string** |  | [optional] 
**LinkType** | **string** |  | 
**MacAddress** | Pointer to **string** |  | [optional] 
**Ipv4Info** | [**[]NodeInterfaceIpv4Info**](NodeInterfaceIpv4Info.md) |  | 
**Ipv6Info** | [**[]NodeInterfaceIpv6Info**](NodeInterfaceIpv6Info.md) |  | 

## Methods

### NewNodeInterface

`func NewNodeInterface(ifname string, operstate string, mtu int32, linkType string, ipv4Info []NodeInterfaceIpv4Info, ipv6Info []NodeInterfaceIpv6Info, ) *NodeInterface`

NewNodeInterface instantiates a new NodeInterface object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNodeInterfaceWithDefaults

`func NewNodeInterfaceWithDefaults() *NodeInterface`

NewNodeInterfaceWithDefaults instantiates a new NodeInterface object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetIfname

`func (o *NodeInterface) GetIfname() string`

GetIfname returns the Ifname field if non-nil, zero value otherwise.

### GetIfnameOk

`func (o *NodeInterface) GetIfnameOk() (*string, bool)`

GetIfnameOk returns a tuple with the Ifname field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIfname

`func (o *NodeInterface) SetIfname(v string)`

SetIfname sets Ifname field to given value.


### GetOperstate

`func (o *NodeInterface) GetOperstate() string`

GetOperstate returns the Operstate field if non-nil, zero value otherwise.

### GetOperstateOk

`func (o *NodeInterface) GetOperstateOk() (*string, bool)`

GetOperstateOk returns a tuple with the Operstate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOperstate

`func (o *NodeInterface) SetOperstate(v string)`

SetOperstate sets Operstate field to given value.


### GetMtu

`func (o *NodeInterface) GetMtu() int32`

GetMtu returns the Mtu field if non-nil, zero value otherwise.

### GetMtuOk

`func (o *NodeInterface) GetMtuOk() (*int32, bool)`

GetMtuOk returns a tuple with the Mtu field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMtu

`func (o *NodeInterface) SetMtu(v int32)`

SetMtu sets Mtu field to given value.


### GetMaster

`func (o *NodeInterface) GetMaster() string`

GetMaster returns the Master field if non-nil, zero value otherwise.

### GetMasterOk

`func (o *NodeInterface) GetMasterOk() (*string, bool)`

GetMasterOk returns a tuple with the Master field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMaster

`func (o *NodeInterface) SetMaster(v string)`

SetMaster sets Master field to given value.

### HasMaster

`func (o *NodeInterface) HasMaster() bool`

HasMaster returns a boolean if a field has been set.

### GetLinkType

`func (o *NodeInterface) GetLinkType() string`

GetLinkType returns the LinkType field if non-nil, zero value otherwise.

### GetLinkTypeOk

`func (o *NodeInterface) GetLinkTypeOk() (*string, bool)`

GetLinkTypeOk returns a tuple with the LinkType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLinkType

`func (o *NodeInterface) SetLinkType(v string)`

SetLinkType sets LinkType field to given value.


### GetMacAddress

`func (o *NodeInterface) GetMacAddress() string`

GetMacAddress returns the MacAddress field if non-nil, zero value otherwise.

### GetMacAddressOk

`func (o *NodeInterface) GetMacAddressOk() (*string, bool)`

GetMacAddressOk returns a tuple with the MacAddress field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMacAddress

`func (o *NodeInterface) SetMacAddress(v string)`

SetMacAddress sets MacAddress field to given value.

### HasMacAddress

`func (o *NodeInterface) HasMacAddress() bool`

HasMacAddress returns a boolean if a field has been set.

### GetIpv4Info

`func (o *NodeInterface) GetIpv4Info() []NodeInterfaceIpv4Info`

GetIpv4Info returns the Ipv4Info field if non-nil, zero value otherwise.

### GetIpv4InfoOk

`func (o *NodeInterface) GetIpv4InfoOk() (*[]NodeInterfaceIpv4Info, bool)`

GetIpv4InfoOk returns a tuple with the Ipv4Info field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIpv4Info

`func (o *NodeInterface) SetIpv4Info(v []NodeInterfaceIpv4Info)`

SetIpv4Info sets Ipv4Info field to given value.


### GetIpv6Info

`func (o *NodeInterface) GetIpv6Info() []NodeInterfaceIpv6Info`

GetIpv6Info returns the Ipv6Info field if non-nil, zero value otherwise.

### GetIpv6InfoOk

`func (o *NodeInterface) GetIpv6InfoOk() (*[]NodeInterfaceIpv6Info, bool)`

GetIpv6InfoOk returns a tuple with the Ipv6Info field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIpv6Info

`func (o *NodeInterface) SetIpv6Info(v []NodeInterfaceIpv6Info)`

SetIpv6Info sets Ipv6Info field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


