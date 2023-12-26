from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.task_incomplete import TaskIncomplete
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    hash_: Union[Unset, None, str] = UNSET,
    admin: Union[Unset, None, bool] = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    params["hash"] = hash_

    params["admin"] = admin

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/api/tasks/incomplete",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, TaskIncomplete]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = TaskIncomplete.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, TaskIncomplete]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    hash_: Union[Unset, None, str] = UNSET,
    admin: Union[Unset, None, bool] = False,
) -> Response[Union[HTTPValidationError, TaskIncomplete]]:
    """Get Tasks Incomplete

    Args:
        hash_ (Union[Unset, None, str]):
        admin (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TaskIncomplete]]
    """

    kwargs = _get_kwargs(
        hash_=hash_,
        admin=admin,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    hash_: Union[Unset, None, str] = UNSET,
    admin: Union[Unset, None, bool] = False,
) -> Optional[Union[HTTPValidationError, TaskIncomplete]]:
    """Get Tasks Incomplete

    Args:
        hash_ (Union[Unset, None, str]):
        admin (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TaskIncomplete]
    """

    return sync_detailed(
        client=client,
        hash_=hash_,
        admin=admin,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    hash_: Union[Unset, None, str] = UNSET,
    admin: Union[Unset, None, bool] = False,
) -> Response[Union[HTTPValidationError, TaskIncomplete]]:
    """Get Tasks Incomplete

    Args:
        hash_ (Union[Unset, None, str]):
        admin (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TaskIncomplete]]
    """

    kwargs = _get_kwargs(
        hash_=hash_,
        admin=admin,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    hash_: Union[Unset, None, str] = UNSET,
    admin: Union[Unset, None, bool] = False,
) -> Optional[Union[HTTPValidationError, TaskIncomplete]]:
    """Get Tasks Incomplete

    Args:
        hash_ (Union[Unset, None, str]):
        admin (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TaskIncomplete]
    """

    return (
        await asyncio_detailed(
            client=client,
            hash_=hash_,
            admin=admin,
        )
    ).parsed
