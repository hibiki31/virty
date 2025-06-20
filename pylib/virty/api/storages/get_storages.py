from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.storage_page import StoragePage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
    node_name: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["page"] = page

    params["admin"] = admin

    json_name_like: Union[None, Unset, str]
    if isinstance(name_like, Unset):
        json_name_like = UNSET
    else:
        json_name_like = name_like
    params["nameLike"] = json_name_like

    json_node_name: Union[None, Unset, str]
    if isinstance(node_name, Unset):
        json_node_name = UNSET
    else:
        json_node_name = node_name
    params["nodeName"] = json_node_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/storages",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, StoragePage]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = StoragePage.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, StoragePage]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
    node_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, StoragePage]]:
    """Get Api Storages

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StoragePage]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
        node_name=node_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
    node_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, StoragePage]]:
    """Get Api Storages

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StoragePage]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
        node_name=node_name,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
    node_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, StoragePage]]:
    """Get Api Storages

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StoragePage]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
        node_name=node_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
    node_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, StoragePage]]:
    """Get Api Storages

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StoragePage]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            page=page,
            admin=admin,
            name_like=name_like,
            node_name=node_name,
        )
    ).parsed
