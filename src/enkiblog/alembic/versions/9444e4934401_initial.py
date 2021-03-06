"""crap

Revision ID: 9444e4934401
Revises: 
Create Date: 2017-06-02 15:32:58.624671

"""

# revision identifiers, used by Alembic.
revision = '9444e4934401'
down_revision = None
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
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', websauna.system.model.columns.UUID(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('created_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('updated_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('group_data', websauna.system.model.columns.JSONB(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_group')),
    sa.UniqueConstraint('name', name=op.f('uq_group_name'))
    )
    op.create_table('tags',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_tags')),
    sa.UniqueConstraint('title', name=op.f('uq_tags_title'))
    )
    op.create_table('user_activation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('updated_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('expires_at', websauna.system.model.columns.UTCDateTime(), nullable=False),
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_activation')),
    sa.UniqueConstraint('code', name=op.f('uq_user_activation_code'))
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', websauna.system.model.columns.UUID(), nullable=True),
    sa.Column('username', sa.String(length=256), nullable=True),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('password', sa.String(length=256), nullable=True),
    sa.Column('created_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('updated_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('activated_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('enabled', sa.Boolean(name='user_enabled_binary'), nullable=True),
    sa.Column('last_login_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('last_login_ip', websauna.system.model.columns.INET(length=50), nullable=True),
    sa.Column('user_data', websauna.system.model.columns.JSONB(), nullable=True),
    sa.Column('last_auth_sensitive_operation_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('activation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['activation_id'], ['user_activation.id'], name=op.f('fk_users_activation_id_user_activation')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    op.create_table('media',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', websauna.system.model.columns.UTCDateTime(), nullable=False),
    sa.Column('published_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('updated_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('mimetype', sa.String(length=256), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('slug', sa.String(length=256), nullable=False),
    sa.Column('blob', postgresql.BYTEA(), nullable=True),
    sa.Column('state', sa.Text(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_media_author_id_users')),
    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_media')),
    sa.UniqueConstraint('slug', name=op.f('uq_media_slug'))
    )
    op.create_table('posts',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', websauna.system.model.columns.UTCDateTime(), nullable=False),
    sa.Column('published_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('updated_at', websauna.system.model.columns.UTCDateTime(), nullable=True),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('slug', sa.String(length=256), nullable=False),
    sa.Column('state', sa.Text(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_posts_author_id_users')),
    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_posts')),
    sa.UniqueConstraint('slug', name=op.f('uq_posts_slug'))
    )
    op.create_table('usergroup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name=op.f('fk_usergroup_group_id_group')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_usergroup_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_usergroup'))
    )
    op.create_table('association_posts_tags',
    sa.Column('post_uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('tag_uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['post_uuid'], ['posts.uuid'], name=op.f('fk_association_posts_tags_post_uuid_posts')),
    sa.ForeignKeyConstraint(['tag_uuid'], ['tags.uuid'], name=op.f('fk_association_posts_tags_tag_uuid_tags')),
    sa.PrimaryKeyConstraint('post_uuid', 'tag_uuid', name=op.f('pk_association_posts_tags'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association_posts_tags')
    op.drop_table('usergroup')
    op.drop_table('posts')
    op.drop_table('media')
    op.drop_table('users')
    op.drop_table('user_activation')
    op.drop_table('tags')
    op.drop_table('group')
    # ### end Alembic commands ###
