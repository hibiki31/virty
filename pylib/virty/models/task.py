import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.task_request import TaskRequest
    from ..models.task_result import TaskResult


T = TypeVar("T", bound="Task")


@_attrs_define
class Task:
    """
    Attributes:
        post_time (Union[Unset, datetime.datetime]):
        run_time (Union[Unset, float]):
        start_time (Union[Unset, datetime.datetime]):
        update_time (Union[Unset, datetime.datetime]):
        user_id (Union[Unset, str]):
        status (Union[Unset, str]):
        resource (Union[Unset, str]):
        object_ (Union[Unset, str]):
        method (Union[Unset, str]):
        dependence_uuid (Union[Unset, str]):
        request (Union[Unset, TaskRequest]):
        result (Union[Unset, TaskResult]):
        message (Union[Unset, str]):
        log (Union[Unset, str]):
        uuid (Union[Unset, str]):
    """

    post_time: Union[Unset, datetime.datetime] = UNSET
    run_time: Union[Unset, float] = UNSET
    start_time: Union[Unset, datetime.datetime] = UNSET
    update_time: Union[Unset, datetime.datetime] = UNSET
    user_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    resource: Union[Unset, str] = UNSET
    object_: Union[Unset, str] = UNSET
    method: Union[Unset, str] = UNSET
    dependence_uuid: Union[Unset, str] = UNSET
    request: Union[Unset, "TaskRequest"] = UNSET
    result: Union[Unset, "TaskResult"] = UNSET
    message: Union[Unset, str] = UNSET
    log: Union[Unset, str] = UNSET
    uuid: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        post_time: Union[Unset, str] = UNSET
        if not isinstance(self.post_time, Unset):
            post_time = self.post_time.isoformat()

        run_time = self.run_time
        start_time: Union[Unset, str] = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        update_time: Union[Unset, str] = UNSET
        if not isinstance(self.update_time, Unset):
            update_time = self.update_time.isoformat()

        user_id = self.user_id
        status = self.status
        resource = self.resource
        object_ = self.object_
        method = self.method
        dependence_uuid = self.dependence_uuid
        request: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.request, Unset):
            request = self.request.to_dict()

        result: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        message = self.message
        log = self.log
        uuid = self.uuid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if post_time is not UNSET:
            field_dict["postTime"] = post_time
        if run_time is not UNSET:
            field_dict["runTime"] = run_time
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if update_time is not UNSET:
            field_dict["updateTime"] = update_time
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if status is not UNSET:
            field_dict["status"] = status
        if resource is not UNSET:
            field_dict["resource"] = resource
        if object_ is not UNSET:
            field_dict["object"] = object_
        if method is not UNSET:
            field_dict["method"] = method
        if dependence_uuid is not UNSET:
            field_dict["dependenceUuid"] = dependence_uuid
        if request is not UNSET:
            field_dict["request"] = request
        if result is not UNSET:
            field_dict["result"] = result
        if message is not UNSET:
            field_dict["message"] = message
        if log is not UNSET:
            field_dict["log"] = log
        if uuid is not UNSET:
            field_dict["uuid"] = uuid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.task_request import TaskRequest
        from ..models.task_result import TaskResult

        d = src_dict.copy()
        _post_time = d.pop("postTime", UNSET)
        post_time: Union[Unset, datetime.datetime]
        if isinstance(_post_time, Unset):
            post_time = UNSET
        else:
            post_time = isoparse(_post_time)

        run_time = d.pop("runTime", UNSET)

        _start_time = d.pop("startTime", UNSET)
        start_time: Union[Unset, datetime.datetime]
        if isinstance(_start_time, Unset):
            start_time = UNSET
        else:
            start_time = isoparse(_start_time)

        _update_time = d.pop("updateTime", UNSET)
        update_time: Union[Unset, datetime.datetime]
        if isinstance(_update_time, Unset):
            update_time = UNSET
        else:
            update_time = isoparse(_update_time)

        user_id = d.pop("userId", UNSET)

        status = d.pop("status", UNSET)

        resource = d.pop("resource", UNSET)

        object_ = d.pop("object", UNSET)

        method = d.pop("method", UNSET)

        dependence_uuid = d.pop("dependenceUuid", UNSET)

        _request = d.pop("request", UNSET)
        request: Union[Unset, TaskRequest]
        if isinstance(_request, Unset):
            request = UNSET
        else:
            request = TaskRequest.from_dict(_request)

        _result = d.pop("result", UNSET)
        result: Union[Unset, TaskResult]
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = TaskResult.from_dict(_result)

        message = d.pop("message", UNSET)

        log = d.pop("log", UNSET)

        uuid = d.pop("uuid", UNSET)

        task = cls(
            post_time=post_time,
            run_time=run_time,
            start_time=start_time,
            update_time=update_time,
            user_id=user_id,
            status=status,
            resource=resource,
            object_=object_,
            method=method,
            dependence_uuid=dependence_uuid,
            request=request,
            result=result,
            message=message,
            log=log,
            uuid=uuid,
        )

        task.additional_properties = d
        return task

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
