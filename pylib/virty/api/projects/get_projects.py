from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.project import Project
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    params["admin"] = admin

    params["limit"] = limit

    params["page"] = page

    params["name"] = name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/api/projects",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, Project]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Project.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, Project]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name: Union[Unset, None, str] = UNSET,
) -> Response[Union[HTTPValidationError, Project]]:
    """Get Api Projects

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Project]]
    """

    kwargs = _get_kwargs(
        admin=admin,
        limit=limit,
        page=page,
        name=name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name: Union[Unset, None, str] = UNSET,
) -> Optional[Union[HTTPValidationError, Project]]:
    """Get Api Projects

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Project]
    """

    return sync_detailed(
        client=client,
        admin=admin,
        limit=limit,
        page=page,
        name=name,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name: Union[Unset, None, str] = UNSET,
) -> Response[Union[HTTPValidationError, Project]]:
    """Get Api Projects

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Project]]
    """

    kwargs = _get_kwargs(
        admin=admin,
        limit=limit,
        page=page,
        name=name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name: Union[Unset, None, str] = UNSET,
) -> Optional[Union[HTTPValidationError, Project]]:
    """Get Api Projects

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Project]
    """

    return (
        await asyncio_detailed(
            client=client,
            admin=admin,
            limit=limit,
            page=page,
            name=name,
        )
    ).parsed
