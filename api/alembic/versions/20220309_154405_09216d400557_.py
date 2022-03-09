"""empty message

Revision ID: 09216d400557
Revises: 946c799e2c8b
Create Date: 2022-03-09 15:44:05.426814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09216d400557'
down_revision = '946c799e2c8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('flavor_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'images', 'flavors', ['flavor_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'images', type_='foreignkey')
    op.drop_column('images', 'flavor_id')
    # ### end Alembic commands ###
