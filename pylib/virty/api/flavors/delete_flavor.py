from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.flavor_page import FlavorPage
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    flavor_id: int,
) -> Dict[str, Any]:
    return {
        "method": "delete",
        "url": "/api/flavors/{flavor_id}".format(
            flavor_id=flavor_id,
        ),
    }


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
    flavor_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[FlavorPage, HTTPValidationError]]:
    """Delete Flavors

    Args:
        flavor_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FlavorPage, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        flavor_id=flavor_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    flavor_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[FlavorPage, HTTPValidationError]]:
    """Delete Flavors

    Args:
        flavor_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FlavorPage, HTTPValidationError]
    """

    return sync_detailed(
        flavor_id=flavor_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    flavor_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[FlavorPage, HTTPValidationError]]:
    """Delete Flavors

    Args:
        flavor_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FlavorPage, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        flavor_id=flavor_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    flavor_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[FlavorPage, HTTPValidationError]]:
    """Delete Flavors

    Args:
        flavor_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FlavorPage, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            flavor_id=flavor_id,
            client=client,
        )
    ).parsed
