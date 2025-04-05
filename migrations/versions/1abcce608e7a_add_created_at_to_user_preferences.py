"""Add created_at to user preferences

Revision ID: 1abcce608e7a
Revises: 
Create Date: 2025-02-28 15:16:31.123456

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '1abcce608e7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 既存のテーブルにcreated_atカラムを追加
    op.add_column('user_preference', sa.Column('created_at', sa.DateTime, nullable=True))
    
    # 既存のレコードのcreated_atを現在時刻で更新
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE user_preference SET created_at = :now WHERE created_at IS NULL"),
        {"now": datetime.utcnow()}
    )
    
    # created_atをNOT NULLに変更
    op.alter_column('user_preference', 'created_at',
                    existing_type=sa.DateTime(),
                    nullable=False)


def downgrade():
    op.drop_column('user_preference', 'created_at')
