"""added user relation to media

Revision ID: fbaf1ab9ae3f
Revises: 2d9085050668
Create Date: 2017-05-28 21:24:19.752372

"""

# revision identifiers, used by Alembic.
revision = 'fbaf1ab9ae3f'
down_revision = '2d9085050668'
branch_labels = None
depends_on = None

import datetime
import websauna.system.model.columns
from sqlalchemy.types import Text  # Needed from proper creation of JSON fields as Alembic inserts astext_type=Text() row

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('group', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('group', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.add_column('media', sa.Column('author_id', sa.Integer(), nullable=True))
    op.alter_column('media', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=False)
    op.alter_column('media', 'published_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('media', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.create_foreign_key(op.f('fk_media_author_id_users'), 'media', 'users', ['author_id'], ['id'])
    op.drop_column('media', 'author')
    op.alter_column('posts', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=False)
    op.alter_column('posts', 'published_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('posts', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('user_activation', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('user_activation', 'expires_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=False)
    op.alter_column('user_activation', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('users', 'activated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('users', 'last_auth_sensitive_operation_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('users', 'last_login_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=websauna.system.model.columns.UTCDateTime(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'updated_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('users', 'last_login_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('users', 'last_auth_sensitive_operation_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('users', 'created_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('users', 'activated_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('user_activation', 'updated_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('user_activation', 'expires_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('user_activation', 'created_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('posts', 'updated_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('posts', 'published_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('posts', 'created_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.add_column('media', sa.Column('author', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    op.drop_constraint(op.f('fk_media_author_id_users'), 'media', type_='foreignkey')
    op.alter_column('media', 'updated_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('media', 'published_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('media', 'created_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_column('media', 'author_id')
    op.alter_column('group', 'updated_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('group', 'created_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    # ### end Alembic commands ###
