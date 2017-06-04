"""updated indexes

Revision ID: 05e45b8e39a6
Revises: 4adfaec7c3ed
Create Date: 2017-06-04 18:02:48.359615

"""

# revision identifiers, used by Alembic.
revision = '05e45b8e39a6'
down_revision = '4adfaec7c3ed'
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
    op.create_index(op.f('ix_media_state'), 'media', ['state'], unique=False)
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
    op.drop_index(op.f('ix_media_state'), table_name='media')
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
    op.alter_column('group', 'updated_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('group', 'created_at',
               existing_type=websauna.system.model.columns.UTCDateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    # ### end Alembic commands ###
