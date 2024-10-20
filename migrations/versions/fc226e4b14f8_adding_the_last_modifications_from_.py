"""adding the last modifications from command and others models

Revision ID: fc226e4b14f8
Revises: 0ae9a65a8ae6
Create Date: 2024-10-13 11:37:33.644315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc226e4b14f8'
down_revision = '0ae9a65a8ae6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_intent', sa.String(length=255), nullable=True))

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint('fk_products_command_id_commands', type_='foreignkey')
        batch_op.drop_column('command_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('command_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_products_command_id_commands', 'commands', ['command_id'], ['id'])

    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.drop_column('payment_intent')

    # ### end Alembic commands ###
