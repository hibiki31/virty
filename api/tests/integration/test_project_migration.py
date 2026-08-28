import importlib.util
from pathlib import Path
from types import ModuleType
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from mixin.database import Engine


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _load_migration() -> ModuleType:
    path = (
        Path(__file__).parents[2]
        / "alembic/versions/20260828_090000_c4e09e71a6b2_unify_project_collaboration.py"
    )
    spec = importlib.util.spec_from_file_location("project_collaboration_migration", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Project migrationを読み込めません")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_legacy_schema(connection: object) -> None:
    execute = getattr(connection, "exec_driver_sql")
    statements = (
        """
        CREATE TABLE projects (
            id VARCHAR(6) PRIMARY KEY,
            name VARCHAR NULL,
            is_admin BOOLEAN NOT NULL,
            core INTEGER NOT NULL,
            memory_g INTEGER NOT NULL,
            storage_capacity_g INTEGER NULL,
            user_installable BOOLEAN NOT NULL
        )
        """,
        "CREATE TABLE users (username VARCHAR PRIMARY KEY)",
        "CREATE TABLE storages_pools (id INTEGER PRIMARY KEY, name VARCHAR)",
        "CREATE TABLE networks_pools (id INTEGER PRIMARY KEY, name VARCHAR)",
        "CREATE TABLE flavors (id INTEGER PRIMARY KEY, name VARCHAR)",
        """
        CREATE TABLE domains (
            uuid VARCHAR PRIMARY KEY,
            owner_user_id VARCHAR NULL REFERENCES users(username) ON DELETE SET NULL,
            owner_project_id VARCHAR(6) NULL,
            CONSTRAINT domains_owner_project_id_fkey
                FOREIGN KEY (owner_project_id) REFERENCES projects(id) ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE projects_ports (
            project_id VARCHAR(6) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            vlan_id INTEGER NOT NULL,
            name VARCHAR,
            PRIMARY KEY (project_id, vlan_id)
        )
        """,
        """
        CREATE TABLE users_to_projects (
            user_id VARCHAR NULL REFERENCES users(username) ON DELETE CASCADE,
            project_id VARCHAR(6) NULL REFERENCES projects(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE projects_to_storages_pools (
            projects_id VARCHAR(6) NULL REFERENCES projects(id) ON DELETE CASCADE,
            storages_pools_id INTEGER NULL REFERENCES storages_pools(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE projects_to_networks_pools (
            projects_id VARCHAR(6) NULL REFERENCES projects(id) ON DELETE CASCADE,
            networks_pools_id INTEGER NULL REFERENCES networks_pools(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE projects_to_flavors_pools (
            projects_id VARCHAR(6) NULL REFERENCES projects(id) ON DELETE CASCADE,
            flavors_id INTEGER NULL REFERENCES flavors(id) ON DELETE CASCADE
        )
        """,
    )
    for statement in statements:
        execute(statement)


def _expect_integrity_error(connection: object, statement: str) -> None:
    begin_nested = getattr(connection, "begin_nested")
    execute = getattr(connection, "execute")
    savepoint = begin_nested()
    try:
        with pytest.raises(IntegrityError):
            execute(text(statement))
    finally:
        savepoint.rollback()


def test_project_migration_preserves_links_and_enforces_ownership(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = f"project_migration_{uuid4().hex}"
    migration = _load_migration()

    with Engine.begin() as connection:
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        _create_legacy_schema(connection)
        connection.execute(text(
            """
            INSERT INTO projects
                (id, name, is_admin, core, memory_g, storage_capacity_g, user_installable)
            VALUES ('abc001', NULL, false, 8, 16, 128, true)
            """
        ))
        connection.execute(text("INSERT INTO users (username) VALUES ('alice')"))
        connection.execute(text("INSERT INTO storages_pools VALUES (1, 'storage')"))
        connection.execute(text("INSERT INTO networks_pools VALUES (2, 'network')"))
        connection.execute(text("INSERT INTO flavors VALUES (3, 'flavor')"))
        for table_name, left_column, right_column, left_value, right_value in (
            ("users_to_projects", "user_id", "project_id", "alice", "abc001"),
            (
                "projects_to_storages_pools",
                "projects_id",
                "storages_pools_id",
                "abc001",
                1,
            ),
            (
                "projects_to_networks_pools",
                "projects_id",
                "networks_pools_id",
                "abc001",
                2,
            ),
            (
                "projects_to_flavors_pools",
                "projects_id",
                "flavors_id",
                "abc001",
                3,
            ),
        ):
            connection.execute(
                text(
                    f'INSERT INTO "{table_name}" '
                    f'("{left_column}", "{right_column}") '
                    f'VALUES (:left_value, :right_value), (:left_value, :right_value)'
                ),
                {"left_value": left_value, "right_value": right_value},
            )
        connection.execute(text(
            """
            INSERT INTO domains (uuid, owner_user_id, owner_project_id)
            VALUES ('vm-1', 'alice', 'abc001')
            """
        ))
        connection.execute(text(
            "INSERT INTO projects_ports VALUES ('abc001', 100, 'legacy')"
        ))

        operations = Operations(MigrationContext.configure(connection))
        monkeypatch.setattr(migration, "op", operations)
        getattr(migration, "upgrade")()

        assert connection.execute(text(
            "SELECT name FROM projects WHERE id = 'abc001'"
        )).scalar_one() == "Project abc001"
        assert connection.execute(text(
            "SELECT owner_user_id FROM domains WHERE uuid = 'vm-1'"
        )).scalar_one_or_none() is None
        for table_name in (
            "users_to_projects",
            "projects_to_storages_pools",
            "projects_to_networks_pools",
            "projects_to_flavors_pools",
        ):
            assert connection.execute(text(
                f'SELECT count(*) FROM "{table_name}"'
            )).scalar_one() == 1
        assert connection.execute(text(
            "SELECT to_regclass('projects_ports')"
        )).scalar_one_or_none() is None
        project_columns = {
            str(value)
            for (value,) in connection.execute(text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = :schema AND table_name = 'projects'
                """
            ), {"schema": schema})
        }
        assert "is_admin" not in project_columns
        assert "user_installable" not in project_columns

        _expect_integrity_error(
            connection,
            "INSERT INTO users_to_projects VALUES ('alice', 'abc001')",
        )
        _expect_integrity_error(
            connection,
            """
            INSERT INTO domains (uuid, owner_user_id, owner_project_id)
            VALUES ('vm-2', 'alice', 'abc001')
            """,
        )
        _expect_integrity_error(
            connection,
            "DELETE FROM projects WHERE id = 'abc001'",
        )

        getattr(migration, "downgrade")()
        assert connection.execute(text(
            "SELECT to_regclass('projects_ports')"
        )).scalar_one() == "projects_ports"
        assert connection.execute(text(
            "SELECT count(*) FROM projects_ports"
        )).scalar_one() == 0
        downgraded_columns = {
            str(value)
            for (value,) in connection.execute(text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = :schema AND table_name = 'projects'
                """
            ), {"schema": schema})
        }
        assert {"is_admin", "user_installable"}.issubset(downgraded_columns)
        delete_rule = connection.execute(text(
            """
            SELECT delete_rule
            FROM information_schema.referential_constraints
            WHERE constraint_schema = :schema
              AND constraint_name = 'domains_owner_project_id_fkey'
            """
        ), {"schema": schema}).scalar_one()
        assert delete_rule == "SET NULL"

        connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')


def test_project_migration_rejects_memberless_project(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = f"project_migration_orphan_{uuid4().hex}"
    migration = _load_migration()

    with Engine.begin() as connection:
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        _create_legacy_schema(connection)
        connection.execute(text(
            """
            INSERT INTO projects
                (id, name, is_admin, core, memory_g, storage_capacity_g, user_installable)
            VALUES ('abc002', 'Orphan', false, 8, 16, 128, true)
            """
        ))

        operations = Operations(MigrationContext.configure(connection))
        monkeypatch.setattr(migration, "op", operations)
        with pytest.raises(RuntimeError, match="memberが0名"):
            getattr(migration, "upgrade")()

        connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
