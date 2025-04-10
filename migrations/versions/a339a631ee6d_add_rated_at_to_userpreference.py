"""Add rated_at to UserPreference

Revision ID: a339a631ee6d
Revises: fa7f9a63803a
Create Date: 2025-03-02 16:16:56.342139

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a339a631ee6d'
down_revision = 'fa7f9a63803a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_preferences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wine_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('rated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['wine_id'], ['wine.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('user_preference')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_preference',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('wine_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('rating', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['wine_id'], ['wine.id'], name='user_preference_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('user_preferences')
    # ### end Alembic commands ###
