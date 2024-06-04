from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.image import Image
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    node_name: Union[Unset, None, str] = UNSET,
    pool_uuid: Union[Unset, None, str] = UNSET,
    name: Union[Unset, None, str] = UNSET,
    rool: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    params["node_name"] = node_name

    params["pool_uuid"] = pool_uuid

    params["name"] = name

    params["rool"] = rool

    params["limit"] = limit

    params["page"] = page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/api/images",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, Image]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Image.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, Image]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    node_name: Union[Unset, None, str] = UNSET,
    pool_uuid: Union[Unset, None, str] = UNSET,
    name: Union[Unset, None, str] = UNSET,
    rool: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
) -> Response[Union[HTTPValidationError, Image]]:
    """Get Api Images

    Args:
        node_name (Union[Unset, None, str]):
        pool_uuid (Union[Unset, None, str]):
        name (Union[Unset, None, str]):
        rool (Union[Unset, None, str]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Image]]
    """

    kwargs = _get_kwargs(
        node_name=node_name,
        pool_uuid=pool_uuid,
        name=name,
        rool=rool,
        limit=limit,
        page=page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    node_name: Union[Unset, None, str] = UNSET,
    pool_uuid: Union[Unset, None, str] = UNSET,
    name: Union[Unset, None, str] = UNSET,
    rool: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
) -> Optional[Union[HTTPValidationError, Image]]:
    """Get Api Images

    Args:
        node_name (Union[Unset, None, str]):
        pool_uuid (Union[Unset, None, str]):
        name (Union[Unset, None, str]):
        rool (Union[Unset, None, str]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Image]
    """

    return sync_detailed(
        client=client,
        node_name=node_name,
        pool_uuid=pool_uuid,
        name=name,
        rool=rool,
        limit=limit,
        page=page,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    node_name: Union[Unset, None, str] = UNSET,
    pool_uuid: Union[Unset, None, str] = UNSET,
    name: Union[Unset, None, str] = UNSET,
    rool: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
) -> Response[Union[HTTPValidationError, Image]]:
    """Get Api Images

    Args:
        node_name (Union[Unset, None, str]):
        pool_uuid (Union[Unset, None, str]):
        name (Union[Unset, None, str]):
        rool (Union[Unset, None, str]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Image]]
    """

    kwargs = _get_kwargs(
        node_name=node_name,
        pool_uuid=pool_uuid,
        name=name,
        rool=rool,
        limit=limit,
        page=page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    node_name: Union[Unset, None, str] = UNSET,
    pool_uuid: Union[Unset, None, str] = UNSET,
    name: Union[Unset, None, str] = UNSET,
    rool: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
) -> Optional[Union[HTTPValidationError, Image]]:
    """Get Api Images

    Args:
        node_name (Union[Unset, None, str]):
        pool_uuid (Union[Unset, None, str]):
        name (Union[Unset, None, str]):
        rool (Union[Unset, None, str]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Image]
    """

    return (
        await asyncio_detailed(
            client=client,
            node_name=node_name,
            pool_uuid=pool_uuid,
            name=name,
            rool=rool,
            limit=limit,
            page=page,
        )
    ).parsed
