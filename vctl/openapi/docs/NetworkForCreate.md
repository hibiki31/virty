# NetworkForCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**NodeName** | **string** |  | 
**Type** | **string** | brdige or ovs | 
**BridgeDevice** | Pointer to **string** |  | [optional] 

## Methods

### NewNetworkForCreate

`func NewNetworkForCreate(name string, nodeName string, type_ string, ) *NetworkForCreate`

NewNetworkForCreate instantiates a new NetworkForCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewNetworkForCreateWithDefaults

`func NewNetworkForCreateWithDefaults() *NetworkForCreate`

NewNetworkForCreateWithDefaults instantiates a new NetworkForCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *NetworkForCreate) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *NetworkForCreate) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *NetworkForCreate) SetName(v string)`

SetName sets Name field to given value.


### GetNodeName

`func (o *NetworkForCreate) GetNodeName() string`

GetNodeName returns the NodeName field if non-nil, zero value otherwise.

### GetNodeNameOk

`func (o *NetworkForCreate) GetNodeNameOk() (*string, bool)`

GetNodeNameOk returns a tuple with the NodeName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNodeName

`func (o *NetworkForCreate) SetNodeName(v string)`

SetNodeName sets NodeName field to given value.


### GetType

`func (o *NetworkForCreate) GetType() string`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *NetworkForCreate) GetTypeOk() (*string, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *NetworkForCreate) SetType(v string)`

SetType sets Type field to given value.


### GetBridgeDevice

`func (o *NetworkForCreate) GetBridgeDevice() string`

GetBridgeDevice returns the BridgeDevice field if non-nil, zero value otherwise.

### GetBridgeDeviceOk

`func (o *NetworkForCreate) GetBridgeDeviceOk() (*string, bool)`

GetBridgeDeviceOk returns a tuple with the BridgeDevice field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBridgeDevice

`func (o *NetworkForCreate) SetBridgeDevice(v string)`

SetBridgeDevice sets BridgeDevice field to given value.

### HasBridgeDevice

`func (o *NetworkForCreate) HasBridgeDevice() bool`

HasBridgeDevice returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


