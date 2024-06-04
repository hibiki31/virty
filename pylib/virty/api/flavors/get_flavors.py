from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.flavor_page import FlavorPage
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/flavors",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[FlavorPage, HTTPValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = FlavorPage.from_dict(response.json())

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
) -> Response[Union[FlavorPage, HTTPValidationError]]:
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
) -> Response[Union[FlavorPage, HTTPValidationError]]:
    """Get Api Flavors

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FlavorPage, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
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
) -> Optional[Union[FlavorPage, HTTPValidationError]]:
    """Get Api Flavors

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FlavorPage, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 25,
    page: Union[Unset, int] = 0,
    admin: Union[Unset, bool] = False,
    name_like: Union[None, Unset, str] = UNSET,
) -> Response[Union[FlavorPage, HTTPValidationError]]:
    """Get Api Flavors

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FlavorPage, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page=page,
        admin=admin,
        name_like=name_like,
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
) -> Optional[Union[FlavorPage, HTTPValidationError]]:
    """Get Api Flavors

    Args:
        limit (Union[Unset, int]):  Default: 25.
        page (Union[Unset, int]):  Default: 0.
        admin (Union[Unset, bool]):  Default: False.
        name_like (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FlavorPage, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            page=page,
            admin=admin,
            name_like=name_like,
        )
    ).parsed
