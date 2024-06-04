from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.network_page import NetworkPage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
    node_name_like: Union[None, Unset, str] = UNSET,
    type: Union[None, Unset, str] = UNSET,
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

    json_node_name_like: Union[None, Unset, str]
    if isinstance(node_name_like, Unset):
        json_node_name_like = UNSET
    else:
        json_node_name_like = node_name_like
    params["nodeNameLike"] = json_node_name_like

    json_type: Union[None, Unset, str]
    if isinstance(type, Unset):
        json_type = UNSET
    else:
        json_type = type
    params["type"] = json_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/networks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, NetworkPage]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = NetworkPage.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, NetworkPage]]:
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
    node_name_like: Union[None, Unset, str] = UNSET,
    type: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, NetworkPage]]:
    """Get Api Networks

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name_like (Union[None, Unset, str]):
        type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, NetworkPage]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
        node_name_like=node_name_like,
        type=type,
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
    node_name_like: Union[None, Unset, str] = UNSET,
    type: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, NetworkPage]]:
    """Get Api Networks

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name_like (Union[None, Unset, str]):
        type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, NetworkPage]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
        node_name_like=node_name_like,
        type=type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
    node_name_like: Union[None, Unset, str] = UNSET,
    type: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, NetworkPage]]:
    """Get Api Networks

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name_like (Union[None, Unset, str]):
        type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, NetworkPage]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
        node_name_like=node_name_like,
        type=type,
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
    node_name_like: Union[None, Unset, str] = UNSET,
    type: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, NetworkPage]]:
    """Get Api Networks

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):
        node_name_like (Union[None, Unset, str]):
        type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, NetworkPage]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            page=page,
            admin=admin,
            name_like=name_like,
            node_name_like=node_name_like,
            type=type,
        )
    ).parsed
