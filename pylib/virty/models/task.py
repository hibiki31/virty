import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.task_result_type_0 import TaskResultType0


T = TypeVar("T", bound="Task")


@_attrs_define
class Task:
    """
    Attributes:
        object_ (str):
        method (str):
        post_time (Union[None, Unset, datetime.datetime]):
        run_time (Union[None, Unset, float]):
        start_time (Union[None, Unset, datetime.datetime]):
        update_time (Union[None, Unset, datetime.datetime]):
        user_id (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        resource (Union[None, Unset, str]):
        dependence_uuid (Union[None, Unset, str]):
        request (Union[Any, None, Unset]):
        result (Union['TaskResultType0', None, Unset]):
        message (Union[None, Unset, str]):
        log (Union[None, Unset, str]):
        uuid (Union[None, Unset, str]):
    """

    object_: str
    method: str
    post_time: Union[None, Unset, datetime.datetime] = UNSET
    run_time: Union[None, Unset, float] = UNSET
    start_time: Union[None, Unset, datetime.datetime] = UNSET
    update_time: Union[None, Unset, datetime.datetime] = UNSET
    user_id: Union[None, Unset, str] = UNSET
    status: Union[None, Unset, str] = UNSET
    resource: Union[None, Unset, str] = UNSET
    dependence_uuid: Union[None, Unset, str] = UNSET
    request: Union[Any, None, Unset] = UNSET
    result: Union["TaskResultType0", None, Unset] = UNSET
    message: Union[None, Unset, str] = UNSET
    log: Union[None, Unset, str] = UNSET
    uuid: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.task_result_type_0 import TaskResultType0

        object_ = self.object_

        method = self.method

        post_time: Union[None, Unset, str]
        if isinstance(self.post_time, Unset):
            post_time = UNSET
        elif isinstance(self.post_time, datetime.datetime):
            post_time = self.post_time.isoformat()
        else:
            post_time = self.post_time

        run_time: Union[None, Unset, float]
        if isinstance(self.run_time, Unset):
            run_time = UNSET
        else:
            run_time = self.run_time

        start_time: Union[None, Unset, str]
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        elif isinstance(self.start_time, datetime.datetime):
            start_time = self.start_time.isoformat()
        else:
            start_time = self.start_time

        update_time: Union[None, Unset, str]
        if isinstance(self.update_time, Unset):
            update_time = UNSET
        elif isinstance(self.update_time, datetime.datetime):
            update_time = self.update_time.isoformat()
        else:
            update_time = self.update_time

        user_id: Union[None, Unset, str]
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        resource: Union[None, Unset, str]
        if isinstance(self.resource, Unset):
            resource = UNSET
        else:
            resource = self.resource

        dependence_uuid: Union[None, Unset, str]
        if isinstance(self.dependence_uuid, Unset):
            dependence_uuid = UNSET
        else:
            dependence_uuid = self.dependence_uuid

        request: Union[Any, None, Unset]
        if isinstance(self.request, Unset):
            request = UNSET
        else:
            request = self.request

        result: Union[Dict[str, Any], None, Unset]
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, TaskResultType0):
            result = self.result.to_dict()
        else:
            result = self.result

        message: Union[None, Unset, str]
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        log: Union[None, Unset, str]
        if isinstance(self.log, Unset):
            log = UNSET
        else:
            log = self.log

        uuid: Union[None, Unset, str]
        if isinstance(self.uuid, Unset):
            uuid = UNSET
        else:
            uuid = self.uuid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "method": method,
            }
        )
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
        from ..models.task_result_type_0 import TaskResultType0

        d = src_dict.copy()
        object_ = d.pop("object")

        method = d.pop("method")

        def _parse_post_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                post_time_type_0 = isoparse(data)

                return post_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        post_time = _parse_post_time(d.pop("postTime", UNSET))

        def _parse_run_time(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        run_time = _parse_run_time(d.pop("runTime", UNSET))

        def _parse_start_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_time_type_0 = isoparse(data)

                return start_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        start_time = _parse_start_time(d.pop("startTime", UNSET))

        def _parse_update_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                update_time_type_0 = isoparse(data)

                return update_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        update_time = _parse_update_time(d.pop("updateTime", UNSET))

        def _parse_user_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_id = _parse_user_id(d.pop("userId", UNSET))

        def _parse_status(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_resource(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        resource = _parse_resource(d.pop("resource", UNSET))

        def _parse_dependence_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        dependence_uuid = _parse_dependence_uuid(d.pop("dependenceUuid", UNSET))

        def _parse_request(data: object) -> Union[Any, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[Any, None, Unset], data)

        request = _parse_request(d.pop("request", UNSET))

        def _parse_result(data: object) -> Union["TaskResultType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = TaskResultType0.from_dict(data)

                return result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TaskResultType0", None, Unset], data)

        result = _parse_result(d.pop("result", UNSET))

        def _parse_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_log(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        log = _parse_log(d.pop("log", UNSET))

        def _parse_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        uuid = _parse_uuid(d.pop("uuid", UNSET))

        task = cls(
            object_=object_,
            method=method,
            post_time=post_time,
            run_time=run_time,
            start_time=start_time,
            update_time=update_time,
            user_id=user_id,
            status=status,
            resource=resource,
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
