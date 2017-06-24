from uuid import uuid4
from collections import namedtuple

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql_dialect
# from sqlalchemy.orm import relationship
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, Deny, DENY_ALL

from websauna.system.model.meta import Base
from websauna.system.model.columns import UTCDateTime
from websauna.utils.time import now
from websauna.system.model.json import NestedMutationDict
from repoze.workflow import get_workflow


P = namedtuple('Permission', ('allowance', 'agents', 'actions'))


def resolve_user_requested_permission_to_states():
    pass


class AssociationPostsTags(Base):
    __tablename__ = "association_posts_tags"
    post_uuid = sa.Column(psql_dialect.UUID(as_uuid=True), sa.ForeignKey('posts.uuid'), primary_key=True)
    tag_uuid = sa.Column(psql_dialect.UUID(as_uuid=True), sa.ForeignKey('tags.uuid'), primary_key=True)


class Post(Base):
    __tablename__ = "posts"

    uuid = sa.Column(psql_dialect.UUID(as_uuid=True), default=uuid4, primary_key=True)

    created_at = sa.Column(UTCDateTime, default=now, nullable=False)
    published_at = sa.Column(UTCDateTime, default=None, nullable=True, index=True)
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    title = sa.Column(sa.String(256), nullable=False)
    description = sa.Column(sa.Text(), nullable=False, default="")

    body = sa.Column(sa.Text(), nullable=False, default="")
    slug = sa.Column(sa.String(256), nullable=False, unique=True)

    # TODO: move all workflow related to json
    #       sa.Column(NestedMutationDict.as_mutable(psql.JSONB), default=dict)
    state = sa.Column(sa.Text(), nullable=False, default="private", index=True)  # TODO: dummy value - get actual default value form config.workflow

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    author = sa.orm.relationship('User')

    tags = sa.orm.relationship(
        'Tag', secondary=AssociationPostsTags.__tablename__, back_populates="posts")

    @property
    def id(self):  # XXX:
        return self.uuid

    def editors(self):
        return (
            self.author,
            'group:admin',
        )

    def __repr__(self):
        return "#{}: {}".format(self.uuid, self.title)

    def __str__(self):
        return self.title


class Media(Base):
    __tablename__ = "media"

    uuid = sa.Column(psql_dialect.UUID(as_uuid=True), default=uuid4, primary_key=True)

    created_at = sa.Column(UTCDateTime, default=now, nullable=False)
    published_at = sa.Column(UTCDateTime, default=None, nullable=True)
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    title = sa.Column(sa.String(256), nullable=False)
    mimetype = sa.Column(sa.String(256), default="")
    description = sa.Column(sa.Text(), nullable=False, default="")
    slug = sa.Column(sa.String(256), nullable=False, unique=True)

    blob = sa.Column(psql_dialect.BYTEA)

    state = sa.Column(sa.Text(), nullable=False, default="private", index=True)

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    author = sa.orm.relationship('User')

    @property
    def id(self):  # XXX:
        return self.uuid

    def editors(self):
        return (
            self.author,
            'group:admin',
        )


class Tag(Base):
    __tablename__ = "tags"

    uuid = sa.Column(psql_dialect.UUID(as_uuid=True), default=uuid4, primary_key=True)

    title = sa.Column(sa.String(256), unique=True, nullable=False)

    posts = sa.orm.relationship(
        'Post', secondary=AssociationPostsTags.__tablename__, back_populates="tags")

    @property
    def id(self):  # XXX:
        return self.uuid

    def __repr__(self):
        return "#{}: {}".format(self.uuid, self.title)

    def __str__(self):
        return self.title
