"""Projectを共同管理境界として正規化する。

Revision ID: c4e09e71a6b2
Revises: a71e4f2d9c30
Create Date: 2026-08-28 09:00:00

"""

from alembic import op
import sqlalchemy as sa


revision = "c4e09e71a6b2"
down_revision = "a71e4f2d9c30"
branch_labels = None
depends_on = None


ASSOCIATIONS = (
    (
        "users_to_projects",
        "user_id",
        "project_id",
        "uq_users_to_projects_user_project",
    ),
    (
        "projects_to_storages_pools",
        "projects_id",
        "storages_pools_id",
        "uq_projects_to_storages_pools_project_pool",
    ),
    (
        "projects_to_networks_pools",
        "projects_id",
        "networks_pools_id",
        "uq_projects_to_networks_pools_project_pool",
    ),
    (
        "projects_to_flavors_pools",
        "projects_id",
        "flavors_id",
        "uq_projects_to_flavors_pools_project_flavor",
    ),
)


def _remove_duplicate_associations(
    table_name: str,
    left_column: str,
    right_column: str,
) -> None:
    op.execute(
        sa.text(
            f'DELETE FROM "{table_name}" '
            f'WHERE "{left_column}" IS NULL OR "{right_column}" IS NULL'
        )
    )
    # Virtyの永続DBはPostgreSQLであり、ctidを使って既存行を1件だけ残す。
    op.execute(
        sa.text(
            f'DELETE FROM "{table_name}" AS older '
            f'USING "{table_name}" AS newer '
            f'WHERE older.ctid < newer.ctid '
            f'AND older."{left_column}" = newer."{left_column}" '
            f'AND older."{right_column}" = newer."{right_column}"'
        )
    )


def _assert_projects_have_members() -> None:
    orphan_ids = [
        str(project_id)
        for (project_id,) in op.get_bind().execute(sa.text(
            "SELECT projects.id FROM projects "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM users_to_projects "
            "WHERE users_to_projects.project_id = projects.id"
            ") ORDER BY projects.id LIMIT 10"
        ))
    ]
    if orphan_ids:
        raise RuntimeError(
            "memberが0名のProjectを移行できません。upgradeを再実行する前に "
            "users_to_projectsへ有効な利用者を1名以上割り当ててください: "
            + ", ".join(orphan_ids)
        )


def upgrade() -> None:
    # 既存名を失わない範囲でtrim・切詰めし、空値だけ安定したfallbackへ補正する。
    op.execute(
        sa.text(
            "UPDATE projects SET name = left(btrim(name), 64) "
            "WHERE name IS NOT NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE projects SET name = 'Project ' || id "
            "WHERE name IS NULL OR name = ''"
        )
    )
    op.alter_column(
        "projects",
        "name",
        existing_type=sa.String(),
        type_=sa.String(length=64),
        nullable=False,
    )
    op.create_check_constraint(
        "ck_projects_name_length",
        "projects",
        "length(trim(name)) BETWEEN 1 AND 64",
    )

    for table_name, left_column, right_column, constraint_name in ASSOCIATIONS:
        _remove_duplicate_associations(table_name, left_column, right_column)
        if table_name == "users_to_projects":
            _assert_projects_have_members()
        op.alter_column(
            table_name,
            left_column,
            existing_type=(
                sa.String()
                if table_name == "users_to_projects"
                else sa.String(length=6)
            ),
            nullable=False,
        )
        right_type = (
            sa.String(length=6)
            if right_column == "project_id"
            else sa.Integer()
        )
        op.alter_column(
            table_name,
            right_column,
            existing_type=right_type,
            nullable=False,
        )
        op.create_unique_constraint(
            constraint_name,
            table_name,
            [left_column, right_column],
        )

    # Project ownerを正本にして、既存の二重ownerを解消する。
    op.execute(
        sa.text(
            "UPDATE domains SET owner_user_id = NULL "
            "WHERE owner_project_id IS NOT NULL"
        )
    )
    op.drop_constraint("domains_owner_project_id_fkey", "domains", type_="foreignkey")
    op.create_foreign_key(
        "domains_owner_project_id_fkey",
        "domains",
        "projects",
        ["owner_project_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "ck_domains_single_owner",
        "domains",
        "NOT (owner_user_id IS NOT NULL AND owner_project_id IS NOT NULL)",
    )

    op.drop_table("projects_ports")
    op.drop_column("projects", "user_installable")
    op.drop_column("projects", "is_admin")


def downgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "user_installable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.alter_column("projects", "is_admin", server_default=None)
    op.alter_column("projects", "user_installable", server_default=None)
    op.create_table(
        "projects_ports",
        sa.Column("project_id", sa.String(length=6), nullable=False),
        sa.Column("vlan_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("project_id", "vlan_id"),
    )

    op.drop_constraint("ck_domains_single_owner", "domains", type_="check")
    op.drop_constraint("domains_owner_project_id_fkey", "domains", type_="foreignkey")
    op.create_foreign_key(
        "domains_owner_project_id_fkey",
        "domains",
        "projects",
        ["owner_project_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    for table_name, left_column, right_column, constraint_name in reversed(ASSOCIATIONS):
        op.drop_constraint(constraint_name, table_name, type_="unique")
        op.alter_column(table_name, left_column, nullable=True)
        op.alter_column(table_name, right_column, nullable=True)

    op.drop_constraint("ck_projects_name_length", "projects", type_="check")
    op.alter_column(
        "projects",
        "name",
        existing_type=sa.String(length=64),
        type_=sa.String(),
        nullable=True,
    )
