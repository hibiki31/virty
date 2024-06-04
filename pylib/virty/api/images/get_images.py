from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.image_page import ImagePage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    node_name: Union[None, Unset, str] = UNSET,
    pool_uuid: Union[None, Unset, str] = UNSET,
    name: Union[None, Unset, str] = UNSET,
    name_like: Union[None, Unset, str] = UNSET,
    rool: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["page"] = page

    params["admin"] = admin

    json_node_name: Union[None, Unset, str]
    if isinstance(node_name, Unset):
        json_node_name = UNSET
    else:
        json_node_name = node_name
    params["nodeName"] = json_node_name

    json_pool_uuid: Union[None, Unset, str]
    if isinstance(pool_uuid, Unset):
        json_pool_uuid = UNSET
    else:
        json_pool_uuid = pool_uuid
    params["poolUuid"] = json_pool_uuid

    json_name: Union[None, Unset, str]
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    json_name_like: Union[None, Unset, str]
    if isinstance(name_like, Unset):
        json_name_like = UNSET
    else:
        json_name_like = name_like
    params["nameLike"] = json_name_like

    json_rool: Union[None, Unset, str]
    if isinstance(rool, Unset):
        json_rool = UNSET
    else:
        json_rool = rool
    params["rool"] = json_rool

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/images",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ImagePage]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ImagePage.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ImagePage]]:
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
    node_name: Union[None, Unset, str] = UNSET,
    pool_uuid: Union[None, Unset, str] = UNSET,
    name: Union[None, Unset, str] = UNSET,
    name_like: Union[None, Unset, str] = UNSET,
    rool: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, ImagePage]]:
    """Get Api Images

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        node_name (Union[None, Unset, str]):
        pool_uuid (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        name_like (Union[None, Unset, str]):
        rool (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ImagePage]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        node_name=node_name,
        pool_uuid=pool_uuid,
        name=name,
        name_like=name_like,
        rool=rool,
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
    node_name: Union[None, Unset, str] = UNSET,
    pool_uuid: Union[None, Unset, str] = UNSET,
    name: Union[None, Unset, str] = UNSET,
    name_like: Union[None, Unset, str] = UNSET,
    rool: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, ImagePage]]:
    """Get Api Images

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        node_name (Union[None, Unset, str]):
        pool_uuid (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        name_like (Union[None, Unset, str]):
        rool (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ImagePage]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        page=page,
        admin=admin,
        node_name=node_name,
        pool_uuid=pool_uuid,
        name=name,
        name_like=name_like,
        rool=rool,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    node_name: Union[None, Unset, str] = UNSET,
    pool_uuid: Union[None, Unset, str] = UNSET,
    name: Union[None, Unset, str] = UNSET,
    name_like: Union[None, Unset, str] = UNSET,
    rool: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, ImagePage]]:
    """Get Api Images

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        node_name (Union[None, Unset, str]):
        pool_uuid (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        name_like (Union[None, Unset, str]):
        rool (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ImagePage]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        node_name=node_name,
        pool_uuid=pool_uuid,
        name=name,
        name_like=name_like,
        rool=rool,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    node_name: Union[None, Unset, str] = UNSET,
    pool_uuid: Union[None, Unset, str] = UNSET,
    name: Union[None, Unset, str] = UNSET,
    name_like: Union[None, Unset, str] = UNSET,
    rool: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, ImagePage]]:
    """Get Api Images

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        node_name (Union[None, Unset, str]):
        pool_uuid (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        name_like (Union[None, Unset, str]):
        rool (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ImagePage]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            page=page,
            admin=admin,
            node_name=node_name,
            pool_uuid=pool_uuid,
            name=name,
            name_like=name_like,
            rool=rool,
        )
    ).parsed
