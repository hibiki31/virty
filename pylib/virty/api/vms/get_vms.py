from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.domain_pagenation import DomainPagenation
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name_like: Union[Unset, None, str] = UNSET,
    node_name_like: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    params["admin"] = admin

    params["limit"] = limit

    params["page"] = page

    params["name_like"] = name_like

    params["node_name_like"] = node_name_like

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/api/vms",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DomainPagenation, HTTPValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = DomainPagenation.from_dict(response.json())

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
) -> Response[Union[DomainPagenation, HTTPValidationError]]:
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
    name_like: Union[Unset, None, str] = UNSET,
    node_name_like: Union[Unset, None, str] = UNSET,
) -> Response[Union[DomainPagenation, HTTPValidationError]]:
    """Get Api Domain

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name_like (Union[Unset, None, str]):
        node_name_like (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DomainPagenation, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        admin=admin,
        limit=limit,
        page=page,
        name_like=name_like,
        node_name_like=node_name_like,
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
    name_like: Union[Unset, None, str] = UNSET,
    node_name_like: Union[Unset, None, str] = UNSET,
) -> Optional[Union[DomainPagenation, HTTPValidationError]]:
    """Get Api Domain

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name_like (Union[Unset, None, str]):
        node_name_like (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DomainPagenation, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        admin=admin,
        limit=limit,
        page=page,
        name_like=name_like,
        node_name_like=node_name_like,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name_like: Union[Unset, None, str] = UNSET,
    node_name_like: Union[Unset, None, str] = UNSET,
) -> Response[Union[DomainPagenation, HTTPValidationError]]:
    """Get Api Domain

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name_like (Union[Unset, None, str]):
        node_name_like (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DomainPagenation, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        admin=admin,
        limit=limit,
        page=page,
        name_like=name_like,
        node_name_like=node_name_like,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    admin: Union[Unset, None, bool] = False,
    limit: Union[Unset, None, int] = 25,
    page: Union[Unset, None, int] = 0,
    name_like: Union[Unset, None, str] = UNSET,
    node_name_like: Union[Unset, None, str] = UNSET,
) -> Optional[Union[DomainPagenation, HTTPValidationError]]:
    """Get Api Domain

    Args:
        admin (Union[Unset, None, bool]):
        limit (Union[Unset, None, int]):  Default: 25.
        page (Union[Unset, None, int]):
        name_like (Union[Unset, None, str]):
        node_name_like (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DomainPagenation, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            admin=admin,
            limit=limit,
            page=page,
            name_like=name_like,
            node_name_like=node_name_like,
        )
    ).parsed
