"""update_sweetness_to_float

Revision ID: f394bac0d1b7
Revises: 1abcce608e7a
Create Date: 2025-02-28 15:47:17.252660

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f394bac0d1b7'
down_revision = '1abcce608e7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wine', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=mysql.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wine', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Integer(),
               type_=mysql.FLOAT(),
               existing_nullable=True)

    # ### end Alembic commands ###
