"""initial

Revision ID: a0792286b5aa
Revises: 
Create Date: 2024-07-17 23:04:19.037382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0792286b5aa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_posts_id', table_name='posts')
    op.drop_index('ix_posts_title', table_name='posts')
    op.drop_table('posts')
    op.drop_index('ix_user_profiles_id', table_name='user_profiles')
    op.drop_table('user_profiles')
    op.drop_index('ix_comments_id', table_name='comments')
    op.drop_table('comments')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=1)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=1)
    op.create_table('comments',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('owner_id', sa.INTEGER(), nullable=True),
    sa.Column('post_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comments_id', 'comments', ['id'], unique=False)
    op.create_table('user_profiles',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('bio', sa.VARCHAR(), nullable=True),
    sa.Column('profile_picture', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_profiles_id', 'user_profiles', ['id'], unique=False)
    op.create_table('posts',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(), nullable=True),
    sa.Column('content', sa.TEXT(), nullable=True),
    sa.Column('owner_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_posts_title', 'posts', ['title'], unique=False)
    op.create_index('ix_posts_id', 'posts', ['id'], unique=False)
    # ### end Alembic commands ###