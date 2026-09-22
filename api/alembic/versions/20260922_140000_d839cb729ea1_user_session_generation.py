"""Web sessionの失効世代を追加する。"""

from alembic import op
import sqlalchemy as sa

revision = "d839cb729ea1"
down_revision = "c4e09e71a6b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 既存ユーザの旧JWTは初回password変更まで受理する。
    op.add_column("users", sa.Column("session_generation", sa.String(36), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "session_generation")
