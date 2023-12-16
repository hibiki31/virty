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

// checks if the ProjectUser type satisfies the MappedNullable interface at compile time
var _ MappedNullable = &ProjectUser{}

// ProjectUser struct for ProjectUser
type ProjectUser struct {
	Username string `json:"username"`
}

type _ProjectUser ProjectUser

// NewProjectUser instantiates a new ProjectUser object
// This constructor will assign default values to properties that have it defined,
// and makes sure properties required by API are set, but the set of arguments
// will change when the set of required properties is changed
func NewProjectUser(username string) *ProjectUser {
	this := ProjectUser{}
	this.Username = username
	return &this
}

// NewProjectUserWithDefaults instantiates a new ProjectUser object
// This constructor will only assign default values to properties that have it defined,
// but it doesn't guarantee that properties required by API are set
func NewProjectUserWithDefaults() *ProjectUser {
	this := ProjectUser{}
	return &this
}

// GetUsername returns the Username field value
func (o *ProjectUser) GetUsername() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.Username
}

// GetUsernameOk returns a tuple with the Username field value
// and a boolean to check if the value has been set.
func (o *ProjectUser) GetUsernameOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.Username, true
}

// SetUsername sets field value
func (o *ProjectUser) SetUsername(v string) {
	o.Username = v
}

func (o ProjectUser) MarshalJSON() ([]byte, error) {
	toSerialize,err := o.ToMap()
	if err != nil {
		return []byte{}, err
	}
	return json.Marshal(toSerialize)
}

func (o ProjectUser) ToMap() (map[string]interface{}, error) {
	toSerialize := map[string]interface{}{}
	toSerialize["username"] = o.Username
	return toSerialize, nil
}

func (o *ProjectUser) UnmarshalJSON(bytes []byte) (err error) {
	// This validates that all required properties are included in the JSON object
	// by unmarshalling the object into a generic map with string keys and checking
	// that every required field exists as a key in the generic map.
	requiredProperties := []string{
		"username",
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

	varProjectUser := _ProjectUser{}

	err = json.Unmarshal(bytes, &varProjectUser)

	if err != nil {
		return err
	}

	*o = ProjectUser(varProjectUser)

	return err
}

type NullableProjectUser struct {
	value *ProjectUser
	isSet bool
}

func (v NullableProjectUser) Get() *ProjectUser {
	return v.value
}

func (v *NullableProjectUser) Set(val *ProjectUser) {
	v.value = val
	v.isSet = true
}

func (v NullableProjectUser) IsSet() bool {
	return v.isSet
}

func (v *NullableProjectUser) Unset() {
	v.value = nil
	v.isSet = false
}

func NewNullableProjectUser(val *ProjectUser) *NullableProjectUser {
	return &NullableProjectUser{value: val, isSet: true}
}

func (v NullableProjectUser) MarshalJSON() ([]byte, error) {
	return json.Marshal(v.value)
}

func (v *NullableProjectUser) UnmarshalJSON(src []byte) error {
	v.isSet = true
	return json.Unmarshal(src, &v.value)
}


