"""addiding some few entry to products

Revision ID: fbbd7212c148
Revises: aabdf4f601cc
Create Date: 2024-10-09 11:06:11.507678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbbd7212c148'
down_revision = 'aabdf4f601cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_summary', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('product_summary')

    # ### end Alembic commands ###
