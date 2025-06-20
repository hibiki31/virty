from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.task_page import TaskPage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    admin: Union[Unset, bool] = False,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    resource: Union[None, Unset, str] = UNSET,
    object_: Union[None, Unset, str] = UNSET,
    method: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["admin"] = admin

    params["limit"] = limit

    params["page"] = page

    json_resource: Union[None, Unset, str]
    if isinstance(resource, Unset):
        json_resource = UNSET
    else:
        json_resource = resource
    params["resource"] = json_resource

    json_object_: Union[None, Unset, str]
    if isinstance(object_, Unset):
        json_object_ = UNSET
    else:
        json_object_ = object_
    params["object"] = json_object_

    json_method: Union[None, Unset, str]
    if isinstance(method, Unset):
        json_method = UNSET
    else:
        json_method = method
    params["method"] = json_method

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/tasks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, TaskPage]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = TaskPage.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, TaskPage]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, bool] = False,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    resource: Union[None, Unset, str] = UNSET,
    object_: Union[None, Unset, str] = UNSET,
    method: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, TaskPage]]:
    """Get Tasks

    Args:
        admin (Union[Unset, bool]):  Default: False.
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        resource (Union[None, Unset, str]):
        object_ (Union[None, Unset, str]):
        method (Union[None, Unset, str]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TaskPage]]
    """

    kwargs = _get_kwargs(
        admin=admin,
        limit=limit,
        page=page,
        resource=resource,
        object_=object_,
        method=method,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, bool] = False,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    resource: Union[None, Unset, str] = UNSET,
    object_: Union[None, Unset, str] = UNSET,
    method: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, TaskPage]]:
    """Get Tasks

    Args:
        admin (Union[Unset, bool]):  Default: False.
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        resource (Union[None, Unset, str]):
        object_ (Union[None, Unset, str]):
        method (Union[None, Unset, str]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TaskPage]
    """

    return sync_detailed(
        client=client,
        admin=admin,
        limit=limit,
        page=page,
        resource=resource,
        object_=object_,
        method=method,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, bool] = False,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    resource: Union[None, Unset, str] = UNSET,
    object_: Union[None, Unset, str] = UNSET,
    method: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, TaskPage]]:
    """Get Tasks

    Args:
        admin (Union[Unset, bool]):  Default: False.
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        resource (Union[None, Unset, str]):
        object_ (Union[None, Unset, str]):
        method (Union[None, Unset, str]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TaskPage]]
    """

    kwargs = _get_kwargs(
        admin=admin,
        limit=limit,
        page=page,
        resource=resource,
        object_=object_,
        method=method,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, bool] = False,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    resource: Union[None, Unset, str] = UNSET,
    object_: Union[None, Unset, str] = UNSET,
    method: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, TaskPage]]:
    """Get Tasks

    Args:
        admin (Union[Unset, bool]):  Default: False.
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        resource (Union[None, Unset, str]):
        object_ (Union[None, Unset, str]):
        method (Union[None, Unset, str]):
        status (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TaskPage]
    """

    return (
        await asyncio_detailed(
            client=client,
            admin=admin,
            limit=limit,
            page=page,
            resource=resource,
            object_=object_,
            method=method,
            status=status,
        )
    ).parsed
