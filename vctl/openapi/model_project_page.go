/*
VirtyAPI

No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

API version: 4.1.0
*/

// Code generated by OpenAPI Generator (https://openapi-generator.tech); DO NOT EDIT.

package openapi

import (
	"encoding/json"
	"fmt"
)

// checks if the ProjectPage type satisfies the MappedNullable interface at compile time
var _ MappedNullable = &ProjectPage{}

// ProjectPage struct for ProjectPage
type ProjectPage struct {
	Id string `json:"id"`
	Name string `json:"name"`
	MemoryG int32 `json:"memoryG"`
	Core int32 `json:"core"`
	StorageCapacityG int32 `json:"storageCapacityG"`
	Users []ProjectUser `json:"users"`
	UsedMemoryG int32 `json:"usedMemoryG"`
	UsedCore int32 `json:"usedCore"`
	NetworkPools interface{} `json:"networkPools,omitempty"`
	StoragePools interface{} `json:"storagePools,omitempty"`
}

type _ProjectPage ProjectPage

// NewProjectPage instantiates a new ProjectPage object
// This constructor will assign default values to properties that have it defined,
// and makes sure properties required by API are set, but the set of arguments
// will change when the set of required properties is changed
func NewProjectPage(id string, name string, memoryG int32, core int32, storageCapacityG int32, users []ProjectUser, usedMemoryG int32, usedCore int32) *ProjectPage {
	this := ProjectPage{}
	this.Id = id
	this.Name = name
	this.MemoryG = memoryG
	this.Core = core
	this.StorageCapacityG = storageCapacityG
	this.Users = users
	this.UsedMemoryG = usedMemoryG
	this.UsedCore = usedCore
	return &this
}

// NewProjectPageWithDefaults instantiates a new ProjectPage object
// This constructor will only assign default values to properties that have it defined,
// but it doesn't guarantee that properties required by API are set
func NewProjectPageWithDefaults() *ProjectPage {
	this := ProjectPage{}
	return &this
}

// GetId returns the Id field value
func (o *ProjectPage) GetId() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.Id
}

// GetIdOk returns a tuple with the Id field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetIdOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.Id, true
}

// SetId sets field value
func (o *ProjectPage) SetId(v string) {
	o.Id = v
}

// GetName returns the Name field value
func (o *ProjectPage) GetName() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.Name
}

// GetNameOk returns a tuple with the Name field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetNameOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.Name, true
}

// SetName sets field value
func (o *ProjectPage) SetName(v string) {
	o.Name = v
}

// GetMemoryG returns the MemoryG field value
func (o *ProjectPage) GetMemoryG() int32 {
	if o == nil {
		var ret int32
		return ret
	}

	return o.MemoryG
}

// GetMemoryGOk returns a tuple with the MemoryG field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetMemoryGOk() (*int32, bool) {
	if o == nil {
		return nil, false
	}
	return &o.MemoryG, true
}

// SetMemoryG sets field value
func (o *ProjectPage) SetMemoryG(v int32) {
	o.MemoryG = v
}

// GetCore returns the Core field value
func (o *ProjectPage) GetCore() int32 {
	if o == nil {
		var ret int32
		return ret
	}

	return o.Core
}

// GetCoreOk returns a tuple with the Core field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetCoreOk() (*int32, bool) {
	if o == nil {
		return nil, false
	}
	return &o.Core, true
}

// SetCore sets field value
func (o *ProjectPage) SetCore(v int32) {
	o.Core = v
}

// GetStorageCapacityG returns the StorageCapacityG field value
func (o *ProjectPage) GetStorageCapacityG() int32 {
	if o == nil {
		var ret int32
		return ret
	}

	return o.StorageCapacityG
}

// GetStorageCapacityGOk returns a tuple with the StorageCapacityG field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetStorageCapacityGOk() (*int32, bool) {
	if o == nil {
		return nil, false
	}
	return &o.StorageCapacityG, true
}

// SetStorageCapacityG sets field value
func (o *ProjectPage) SetStorageCapacityG(v int32) {
	o.StorageCapacityG = v
}

// GetUsers returns the Users field value
func (o *ProjectPage) GetUsers() []ProjectUser {
	if o == nil {
		var ret []ProjectUser
		return ret
	}

	return o.Users
}

// GetUsersOk returns a tuple with the Users field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetUsersOk() ([]ProjectUser, bool) {
	if o == nil {
		return nil, false
	}
	return o.Users, true
}

// SetUsers sets field value
func (o *ProjectPage) SetUsers(v []ProjectUser) {
	o.Users = v
}

// GetUsedMemoryG returns the UsedMemoryG field value
func (o *ProjectPage) GetUsedMemoryG() int32 {
	if o == nil {
		var ret int32
		return ret
	}

	return o.UsedMemoryG
}

// GetUsedMemoryGOk returns a tuple with the UsedMemoryG field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetUsedMemoryGOk() (*int32, bool) {
	if o == nil {
		return nil, false
	}
	return &o.UsedMemoryG, true
}

// SetUsedMemoryG sets field value
func (o *ProjectPage) SetUsedMemoryG(v int32) {
	o.UsedMemoryG = v
}

// GetUsedCore returns the UsedCore field value
func (o *ProjectPage) GetUsedCore() int32 {
	if o == nil {
		var ret int32
		return ret
	}

	return o.UsedCore
}

// GetUsedCoreOk returns a tuple with the UsedCore field value
// and a boolean to check if the value has been set.
func (o *ProjectPage) GetUsedCoreOk() (*int32, bool) {
	if o == nil {
		return nil, false
	}
	return &o.UsedCore, true
}

// SetUsedCore sets field value
func (o *ProjectPage) SetUsedCore(v int32) {
	o.UsedCore = v
}

// GetNetworkPools returns the NetworkPools field value if set, zero value otherwise (both if not set or set to explicit null).
func (o *ProjectPage) GetNetworkPools() interface{} {
	if o == nil {
		var ret interface{}
		return ret
	}
	return o.NetworkPools
}

// GetNetworkPoolsOk returns a tuple with the NetworkPools field value if set, nil otherwise
// and a boolean to check if the value has been set.
// NOTE: If the value is an explicit nil, `nil, true` will be returned
func (o *ProjectPage) GetNetworkPoolsOk() (*interface{}, bool) {
	if o == nil || IsNil(o.NetworkPools) {
		return nil, false
	}
	return &o.NetworkPools, true
}

// HasNetworkPools returns a boolean if a field has been set.
func (o *ProjectPage) HasNetworkPools() bool {
	if o != nil && IsNil(o.NetworkPools) {
		return true
	}

	return false
}

// SetNetworkPools gets a reference to the given interface{} and assigns it to the NetworkPools field.
func (o *ProjectPage) SetNetworkPools(v interface{}) {
	o.NetworkPools = v
}

// GetStoragePools returns the StoragePools field value if set, zero value otherwise (both if not set or set to explicit null).
func (o *ProjectPage) GetStoragePools() interface{} {
	if o == nil {
		var ret interface{}
		return ret
	}
	return o.StoragePools
}

// GetStoragePoolsOk returns a tuple with the StoragePools field value if set, nil otherwise
// and a boolean to check if the value has been set.
// NOTE: If the value is an explicit nil, `nil, true` will be returned
func (o *ProjectPage) GetStoragePoolsOk() (*interface{}, bool) {
	if o == nil || IsNil(o.StoragePools) {
		return nil, false
	}
	return &o.StoragePools, true
}

// HasStoragePools returns a boolean if a field has been set.
func (o *ProjectPage) HasStoragePools() bool {
	if o != nil && IsNil(o.StoragePools) {
		return true
	}

	return false
}

// SetStoragePools gets a reference to the given interface{} and assigns it to the StoragePools field.
func (o *ProjectPage) SetStoragePools(v interface{}) {
	o.StoragePools = v
}

func (o ProjectPage) MarshalJSON() ([]byte, error) {
	toSerialize,err := o.ToMap()
	if err != nil {
		return []byte{}, err
	}
	return json.Marshal(toSerialize)
}

func (o ProjectPage) ToMap() (map[string]interface{}, error) {
	toSerialize := map[string]interface{}{}
	toSerialize["id"] = o.Id
	toSerialize["name"] = o.Name
	toSerialize["memoryG"] = o.MemoryG
	toSerialize["core"] = o.Core
	toSerialize["storageCapacityG"] = o.StorageCapacityG
	toSerialize["users"] = o.Users
	toSerialize["usedMemoryG"] = o.UsedMemoryG
	toSerialize["usedCore"] = o.UsedCore
	if o.NetworkPools != nil {
		toSerialize["networkPools"] = o.NetworkPools
	}
	if o.StoragePools != nil {
		toSerialize["storagePools"] = o.StoragePools
	}
	return toSerialize, nil
}

func (o *ProjectPage) UnmarshalJSON(bytes []byte) (err error) {
	// This validates that all required properties are included in the JSON object
	// by unmarshalling the object into a generic map with string keys and checking
	// that every required field exists as a key in the generic map.
	requiredProperties := []string{
		"id",
		"name",
		"memoryG",
		"core",
		"storageCapacityG",
		"users",
		"usedMemoryG",
		"usedCore",
	}

	allProperties := make(map[string]interface{})

	err = json.Unmarshal(bytes, &allProperties)

	if err != nil {
		return err;
	}

	for _, requiredProperty := range(requiredProperties) {
		if _, exists := allProperties[requiredProperty]; !exists {
			return fmt.Errorf("no value given for required property %v", requiredProperty)
		}
	}

	varProjectPage := _ProjectPage{}

	err = json.Unmarshal(bytes, &varProjectPage)

	if err != nil {
		return err
	}

	*o = ProjectPage(varProjectPage)

	return err
}

type NullableProjectPage struct {
	value *ProjectPage
	isSet bool
}

func (v NullableProjectPage) Get() *ProjectPage {
	return v.value
}

func (v *NullableProjectPage) Set(val *ProjectPage) {
	v.value = val
	v.isSet = true
}

func (v NullableProjectPage) IsSet() bool {
	return v.isSet
}

func (v *NullableProjectPage) Unset() {
	v.value = nil
	v.isSet = false
}

func NewNullableProjectPage(val *ProjectPage) *NullableProjectPage {
	return &NullableProjectPage{value: val, isSet: true}
}

func (v NullableProjectPage) MarshalJSON() ([]byte, error) {
	return json.Marshal(v.value)
}

func (v *NullableProjectPage) UnmarshalJSON(src []byte) error {
	v.isSet = true
	return json.Unmarshal(src, &v.value)
}


