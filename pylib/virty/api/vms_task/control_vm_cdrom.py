from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cdrom_for_update_domain import CdromForUpdateDomain
from ...models.http_validation_error import HTTPValidationError
from ...models.task import Task
from ...types import Response


def _get_kwargs(
    uuid: str,
    *,
    json_body: CdromForUpdateDomain,
) -> Dict[str, Any]:
    json_json_body = json_body.to_dict()

    return {
        "method": "patch",
        "url": "/api/tasks/vms/{uuid}/cdrom".format(
            uuid=uuid,
        ),
        "json": json_json_body,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, List["Task"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Task.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[HTTPValidationError, List["Task"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uuid: str,
    *,
    client: AuthenticatedClient,
    json_body: CdromForUpdateDomain,
) -> Response[Union[HTTPValidationError, List["Task"]]]:
    """Patch Api Tasks Vms Uuid Cdrom

     umount
    - path = null

    mount
    - path = iso file path

    Args:
        uuid (str):
        json_body (CdromForUpdateDomain):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, List['Task']]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        json_body=json_body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: str,
    *,
    client: AuthenticatedClient,
    json_body: CdromForUpdateDomain,
) -> Optional[Union[HTTPValidationError, List["Task"]]]:
    """Patch Api Tasks Vms Uuid Cdrom

     umount
    - path = null

    mount
    - path = iso file path

    Args:
        uuid (str):
        json_body (CdromForUpdateDomain):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, List['Task']]
    """

    return sync_detailed(
        uuid=uuid,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    uuid: str,
    *,
    client: AuthenticatedClient,
    json_body: CdromForUpdateDomain,
) -> Response[Union[HTTPValidationError, List["Task"]]]:
    """Patch Api Tasks Vms Uuid Cdrom

     umount
    - path = null

    mount
    - path = iso file path

    Args:
        uuid (str):
        json_body (CdromForUpdateDomain):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, List['Task']]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: str,
    *,
    client: AuthenticatedClient,
    json_body: CdromForUpdateDomain,
) -> Optional[Union[HTTPValidationError, List["Task"]]]:
    """Patch Api Tasks Vms Uuid Cdrom

     umount
    - path = null

    mount
    - path = iso file path

    Args:
        uuid (str):
        json_body (CdromForUpdateDomain):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, List['Task']]
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            json_body=json_body,
        )
    ).parsed