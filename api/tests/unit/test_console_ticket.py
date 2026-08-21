import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

from auth.router import CurrentUser
from domain import router
from domain.models import DomainConsoleTicketModel, DomainModel
from domain.security import scrub_domain_xml_directory
from main import _ConsoleTicketAccessLogFilter
from module.xmllib import redact_domain_xml_secrets


class _CreateSession:
    def __init__(self) -> None:
        self.added: DomainConsoleTicketModel | None = None
        self.commits = 0

    def add(self, model: DomainConsoleTicketModel) -> None:
        self.added = model

    def query(self, model: type[Any]) -> "_Query":
        assert model is DomainConsoleTicketModel
        return _Query(None)

    def commit(self) -> None:
        self.commits += 1


class _Query:
    def __init__(self, value: Any) -> None:
        self.value = value

    def filter(self, *_args: object) -> "_Query":
        return self

    def with_for_update(self) -> "_Query":
        return self

    def one_or_none(self) -> Any:
        return self.value

    def delete(self, *, synchronize_session: bool) -> int:
        assert synchronize_session is False
        return 0


class _ResolveSession:
    def __init__(self, ticket: Any, domain: Any) -> None:
        self.ticket = ticket
        self.domain = domain
        self.commits = 0

    def query(self, model: type[Any]) -> _Query:
        if model is DomainConsoleTicketModel:
            return _Query(self.ticket)
        if model is DomainModel:
            return _Query(self.domain)
        raise AssertionError(f"unexpected model: {model}")

    def commit(self) -> None:
        self.commits += 1


def test_console_ticket_is_opaque_and_single_use(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_db = _CreateSession()
    user = CurrentUser(id="alice", token="token", scopes=["vm.read"])
    monkeypatch.setattr(router, "get_authorized_domain", lambda *_args: object())

    http_response = Response()
    ticket = router.create_console_ticket(
        "vm-1",
        response=http_response,
        current_user=user,
        db=cast(Session, create_db),
    )

    assert create_db.added is not None
    assert create_db.added.token_hash != ticket.token
    assert ticket.token not in create_db.added.token_hash
    assert create_db.commits == 1
    assert http_response.headers["cache-control"] == "no-store"

    domain = SimpleNamespace(node=SimpleNamespace(domain="node.internal"), vnc_port=5900)
    resolve_db = _ResolveSession(create_db.added, domain)
    assert router.get_vnc_address(ticket.token, db=cast(Session, resolve_db)) == {
        "host": "node.internal",
        "port": 5900,
    }
    assert create_db.added.used_at is not None
    assert resolve_db.commits == 1

    with pytest.raises(HTTPException) as exc_info:
        router.get_vnc_address(ticket.token, db=cast(Session, resolve_db))
    assert exc_info.value.status_code == 401


def test_domain_xml_does_not_expose_vnc_password() -> None:
    result = redact_domain_xml_secrets(
        '<domain><devices><graphics type="vnc" passwd="secret-value" '
        'passwdValidTo="tomorrow" port="5900"/></devices></domain>'
    )

    assert "secret-value" not in result
    assert "passwd" not in result
    assert 'port="5900"' in result


def test_console_ticket_path_is_suppressed_from_uvicorn_access_log() -> None:
    ticket_record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        __file__,
        1,
        '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1", "GET", "/api/vms/vnc/opaque-secret", "1.1", 200),
        None,
    )
    ordinary_record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        __file__,
        1,
        '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1", "GET", "/api/vms/vm-1", "1.1", 200),
        None,
    )

    access_filter = _ConsoleTicketAccessLogFilter()
    assert access_filter.filter(ticket_record) is False
    assert access_filter.filter(ordinary_record) is True


def test_existing_domain_xml_is_scrubbed_on_startup(tmp_path: Path) -> None:
    directory = tmp_path / "xml" / "domain"
    directory.mkdir(parents=True)
    xml_path = directory / "vm-1.xml"
    xml_path.write_text(
        '<domain><devices><graphics type="vnc" passwd="old-secret"/></devices></domain>',
        encoding="utf-8",
    )

    assert scrub_domain_xml_directory(str(tmp_path)) == 1
    assert "old-secret" not in xml_path.read_text(encoding="utf-8")
    assert xml_path.stat().st_mode & 0o777 == 0o600
    assert scrub_domain_xml_directory(str(tmp_path)) == 0
