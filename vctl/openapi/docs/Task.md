# Task

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**PostTime** | Pointer to **time.Time** |  | [optional] 
**RunTime** | Pointer to **float32** |  | [optional] 
**StartTime** | Pointer to **time.Time** |  | [optional] 
**UpdateTime** | Pointer to **time.Time** |  | [optional] 
**UserId** | Pointer to **string** |  | [optional] 
**Status** | Pointer to **string** |  | [optional] 
**Resource** | Pointer to **string** |  | [optional] 
**Object** | Pointer to **string** |  | [optional] 
**Method** | Pointer to **string** |  | [optional] 
**DependenceUuid** | Pointer to **string** |  | [optional] 
**Request** | Pointer to **map[string]interface{}** |  | [optional] 
**Result** | Pointer to **map[string]interface{}** |  | [optional] 
**Message** | Pointer to **string** |  | [optional] 
**Log** | Pointer to **string** |  | [optional] 
**Uuid** | Pointer to **string** |  | [optional] 

## Methods

### NewTask

`func NewTask() *Task`

NewTask instantiates a new Task object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewTaskWithDefaults

`func NewTaskWithDefaults() *Task`

NewTaskWithDefaults instantiates a new Task object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPostTime

`func (o *Task) GetPostTime() time.Time`

GetPostTime returns the PostTime field if non-nil, zero value otherwise.

### GetPostTimeOk

`func (o *Task) GetPostTimeOk() (*time.Time, bool)`

GetPostTimeOk returns a tuple with the PostTime field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPostTime

`func (o *Task) SetPostTime(v time.Time)`

SetPostTime sets PostTime field to given value.

### HasPostTime

`func (o *Task) HasPostTime() bool`

HasPostTime returns a boolean if a field has been set.

### GetRunTime

`func (o *Task) GetRunTime() float32`

GetRunTime returns the RunTime field if non-nil, zero value otherwise.

### GetRunTimeOk

`func (o *Task) GetRunTimeOk() (*float32, bool)`

GetRunTimeOk returns a tuple with the RunTime field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRunTime

`func (o *Task) SetRunTime(v float32)`

SetRunTime sets RunTime field to given value.

### HasRunTime

`func (o *Task) HasRunTime() bool`

HasRunTime returns a boolean if a field has been set.

### GetStartTime

`func (o *Task) GetStartTime() time.Time`

GetStartTime returns the StartTime field if non-nil, zero value otherwise.

### GetStartTimeOk

`func (o *Task) GetStartTimeOk() (*time.Time, bool)`

GetStartTimeOk returns a tuple with the StartTime field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStartTime

`func (o *Task) SetStartTime(v time.Time)`

SetStartTime sets StartTime field to given value.

### HasStartTime

`func (o *Task) HasStartTime() bool`

HasStartTime returns a boolean if a field has been set.

### GetUpdateTime

`func (o *Task) GetUpdateTime() time.Time`

GetUpdateTime returns the UpdateTime field if non-nil, zero value otherwise.

### GetUpdateTimeOk

`func (o *Task) GetUpdateTimeOk() (*time.Time, bool)`

GetUpdateTimeOk returns a tuple with the UpdateTime field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUpdateTime

`func (o *Task) SetUpdateTime(v time.Time)`

SetUpdateTime sets UpdateTime field to given value.

### HasUpdateTime

`func (o *Task) HasUpdateTime() bool`

HasUpdateTime returns a boolean if a field has been set.

### GetUserId

`func (o *Task) GetUserId() string`

GetUserId returns the UserId field if non-nil, zero value otherwise.

### GetUserIdOk

`func (o *Task) GetUserIdOk() (*string, bool)`

GetUserIdOk returns a tuple with the UserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserId

`func (o *Task) SetUserId(v string)`

SetUserId sets UserId field to given value.

### HasUserId

`func (o *Task) HasUserId() bool`

HasUserId returns a boolean if a field has been set.

### GetStatus

`func (o *Task) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *Task) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *Task) SetStatus(v string)`

SetStatus sets Status field to given value.

### HasStatus

`func (o *Task) HasStatus() bool`

HasStatus returns a boolean if a field has been set.

### GetResource

`func (o *Task) GetResource() string`

GetResource returns the Resource field if non-nil, zero value otherwise.

### GetResourceOk

`func (o *Task) GetResourceOk() (*string, bool)`

GetResourceOk returns a tuple with the Resource field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResource

`func (o *Task) SetResource(v string)`

SetResource sets Resource field to given value.

### HasResource

`func (o *Task) HasResource() bool`

HasResource returns a boolean if a field has been set.

### GetObject

`func (o *Task) GetObject() string`

GetObject returns the Object field if non-nil, zero value otherwise.

### GetObjectOk

`func (o *Task) GetObjectOk() (*string, bool)`

GetObjectOk returns a tuple with the Object field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetObject

`func (o *Task) SetObject(v string)`

SetObject sets Object field to given value.

### HasObject

`func (o *Task) HasObject() bool`

HasObject returns a boolean if a field has been set.

### GetMethod

`func (o *Task) GetMethod() string`

GetMethod returns the Method field if non-nil, zero value otherwise.

### GetMethodOk

`func (o *Task) GetMethodOk() (*string, bool)`

GetMethodOk returns a tuple with the Method field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMethod

`func (o *Task) SetMethod(v string)`

SetMethod sets Method field to given value.

### HasMethod

`func (o *Task) HasMethod() bool`

HasMethod returns a boolean if a field has been set.

### GetDependenceUuid

`func (o *Task) GetDependenceUuid() string`

GetDependenceUuid returns the DependenceUuid field if non-nil, zero value otherwise.

### GetDependenceUuidOk

`func (o *Task) GetDependenceUuidOk() (*string, bool)`

GetDependenceUuidOk returns a tuple with the DependenceUuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDependenceUuid

`func (o *Task) SetDependenceUuid(v string)`

SetDependenceUuid sets DependenceUuid field to given value.

### HasDependenceUuid

`func (o *Task) HasDependenceUuid() bool`

HasDependenceUuid returns a boolean if a field has been set.

### GetRequest

`func (o *Task) GetRequest() map[string]interface{}`

GetRequest returns the Request field if non-nil, zero value otherwise.

### GetRequestOk

`func (o *Task) GetRequestOk() (*map[string]interface{}, bool)`

GetRequestOk returns a tuple with the Request field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRequest

`func (o *Task) SetRequest(v map[string]interface{})`

SetRequest sets Request field to given value.

### HasRequest

`func (o *Task) HasRequest() bool`

HasRequest returns a boolean if a field has been set.

### GetResult

`func (o *Task) GetResult() map[string]interface{}`

GetResult returns the Result field if non-nil, zero value otherwise.

### GetResultOk

`func (o *Task) GetResultOk() (*map[string]interface{}, bool)`

GetResultOk returns a tuple with the Result field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResult

`func (o *Task) SetResult(v map[string]interface{})`

SetResult sets Result field to given value.

### HasResult

`func (o *Task) HasResult() bool`

HasResult returns a boolean if a field has been set.

### GetMessage

`func (o *Task) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *Task) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *Task) SetMessage(v string)`

SetMessage sets Message field to given value.

### HasMessage

`func (o *Task) HasMessage() bool`

HasMessage returns a boolean if a field has been set.

### GetLog

`func (o *Task) GetLog() string`

GetLog returns the Log field if non-nil, zero value otherwise.

### GetLogOk

`func (o *Task) GetLogOk() (*string, bool)`

GetLogOk returns a tuple with the Log field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLog

`func (o *Task) SetLog(v string)`

SetLog sets Log field to given value.

### HasLog

`func (o *Task) HasLog() bool`

HasLog returns a boolean if a field has been set.

### GetUuid

`func (o *Task) GetUuid() string`

GetUuid returns the Uuid field if non-nil, zero value otherwise.

### GetUuidOk

`func (o *Task) GetUuidOk() (*string, bool)`

GetUuidOk returns a tuple with the Uuid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUuid

`func (o *Task) SetUuid(v string)`

SetUuid sets Uuid field to given value.

### HasUuid

`func (o *Task) HasUuid() bool`

HasUuid returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


