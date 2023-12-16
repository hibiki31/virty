# DomainForCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Type** | **string** |  | 
**Name** | **string** |  | 
**NodeName** | **string** |  | 
**MemoryMegaByte** | **int32** |  | 
**Cpu** | **int32** |  | 
**Disks** | [**[]DomainForCreateDisk**](DomainForCreateDisk.md) |  | 
**Interface** | [**[]DomainForCreateInterface**](DomainForCreateInterface.md) |  | 
**CloudInit** | Pointer to [**CloudInitInsert**](CloudInitInsert.md) |  | [optional] 

## Methods

### NewDomainForCreate

`func NewDomainForCreate(type_ string, name string, nodeName string, memoryMegaByte int32, cpu int32, disks []DomainForCreateDisk, interface_ []DomainForCreateInterface, ) *DomainForCreate`

NewDomainForCreate instantiates a new DomainForCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDomainForCreateWithDefaults

`func NewDomainForCreateWithDefaults() *DomainForCreate`

NewDomainForCreateWithDefaults instantiates a new DomainForCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetType

`func (o *DomainForCreate) GetType() string`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *DomainForCreate) GetTypeOk() (*string, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *DomainForCreate) SetType(v string)`

SetType sets Type field to given value.


### GetName

`func (o *DomainForCreate) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *DomainForCreate) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *DomainForCreate) SetName(v string)`

SetName sets Name field to given value.


### GetNodeName

`func (o *DomainForCreate) GetNodeName() string`

GetNodeName returns the NodeName field if non-nil, zero value otherwise.

### GetNodeNameOk

`func (o *DomainForCreate) GetNodeNameOk() (*string, bool)`

GetNodeNameOk returns a tuple with the NodeName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNodeName

`func (o *DomainForCreate) SetNodeName(v string)`

SetNodeName sets NodeName field to given value.


### GetMemoryMegaByte

`func (o *DomainForCreate) GetMemoryMegaByte() int32`

GetMemoryMegaByte returns the MemoryMegaByte field if non-nil, zero value otherwise.

### GetMemoryMegaByteOk

`func (o *DomainForCreate) GetMemoryMegaByteOk() (*int32, bool)`

GetMemoryMegaByteOk returns a tuple with the MemoryMegaByte field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemoryMegaByte

`func (o *DomainForCreate) SetMemoryMegaByte(v int32)`

SetMemoryMegaByte sets MemoryMegaByte field to given value.


### GetCpu

`func (o *DomainForCreate) GetCpu() int32`

GetCpu returns the Cpu field if non-nil, zero value otherwise.

### GetCpuOk

`func (o *DomainForCreate) GetCpuOk() (*int32, bool)`

GetCpuOk returns a tuple with the Cpu field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCpu

`func (o *DomainForCreate) SetCpu(v int32)`

SetCpu sets Cpu field to given value.


### GetDisks

`func (o *DomainForCreate) GetDisks() []DomainForCreateDisk`

GetDisks returns the Disks field if non-nil, zero value otherwise.

### GetDisksOk

`func (o *DomainForCreate) GetDisksOk() (*[]DomainForCreateDisk, bool)`

GetDisksOk returns a tuple with the Disks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDisks

`func (o *DomainForCreate) SetDisks(v []DomainForCreateDisk)`

SetDisks sets Disks field to given value.


### GetInterface

`func (o *DomainForCreate) GetInterface() []DomainForCreateInterface`

GetInterface returns the Interface field if non-nil, zero value otherwise.

### GetInterfaceOk

`func (o *DomainForCreate) GetInterfaceOk() (*[]DomainForCreateInterface, bool)`

GetInterfaceOk returns a tuple with the Interface field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInterface

`func (o *DomainForCreate) SetInterface(v []DomainForCreateInterface)`

SetInterface sets Interface field to given value.


### GetCloudInit

`func (o *DomainForCreate) GetCloudInit() CloudInitInsert`

GetCloudInit returns the CloudInit field if non-nil, zero value otherwise.

### GetCloudInitOk

`func (o *DomainForCreate) GetCloudInitOk() (*CloudInitInsert, bool)`

GetCloudInitOk returns a tuple with the CloudInit field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCloudInit

`func (o *DomainForCreate) SetCloudInit(v CloudInitInsert)`

SetCloudInit sets CloudInit field to given value.

### HasCloudInit

`func (o *DomainForCreate) HasCloudInit() bool`

HasCloudInit returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


