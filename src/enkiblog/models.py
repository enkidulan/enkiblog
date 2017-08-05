# pylint: disable=too-few-public-methods
from uuid import uuid4
from collections import namedtuple

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql_dialect

from websauna.system.model.meta import Base
from websauna.system.model.columns import UTCDateTime
from websauna.utils.time import now


P = namedtuple('Permission', ('allowance', 'agents', 'actions'))


class AssociationPostsTags(Base):
    __tablename__ = "association_posts_tags"

    post_uuid = sa.Column(
        psql_dialect.UUID(as_uuid=True), sa.ForeignKey('posts.uuid'), primary_key=True)
    tag_uuid = sa.Column(
        psql_dialect.UUID(as_uuid=True), sa.ForeignKey('tags.uuid'), primary_key=True)


class Post(Base):
    __tablename__ = "posts"

    uuid = sa.Column(psql_dialect.UUID(as_uuid=True), default=uuid4, primary_key=True)

    created_at = sa.Column(UTCDateTime, default=now, nullable=False)

    # TODO: on uniques of `published_at` depend reliability of view prev/next feature
    published_at = sa.Column(UTCDateTime, default=None, nullable=True, index=True, unique=True)
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    title = sa.Column(sa.String(256), nullable=False)
    description = sa.Column(sa.Text(), nullable=False, default="")

    body = sa.Column(sa.Text(), nullable=False, default="")
    slug = sa.Column(sa.String(256), nullable=False, unique=True)

    # TODO: dummy value - get actual default value form config.workflow
    state = sa.Column(sa.Text(), nullable=False, default="private", index=True)

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    author = sa.orm.relationship('User')

    tags = sa.orm.relationship(
        'Tag', secondary=AssociationPostsTags.__tablename__, back_populates="posts")

    def editors(self):
        return (self.author, 'group:admin',)

    def __repr__(self):
        return "#{}: {}".format(self.uuid, self.title)

    def __str__(self):
        return self.title

    @property
    def id(self):  # pylint: disable=invalid-name
       # TODO: hack for compatibility with websauna admin crud, rewrite
        return self.uuid

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

    def editors(self):
        return (self.author, 'group:admin')

    @property
    def id(self):  # pylint: disable=invalid-name
       # TODO: hack for compatibility with websauna admin crud, rewrite
        return self.uuid



class Tag(Base):
    __tablename__ = "tags"

    uuid = sa.Column(psql_dialect.UUID(as_uuid=True), default=uuid4, primary_key=True)

    title = sa.Column(sa.String(256), unique=True, nullable=False)

    posts = sa.orm.relationship(
        'Post', secondary=AssociationPostsTags.__tablename__, back_populates="tags")

    def __repr__(self):
        return "#{}: {}".format(self.uuid, self.title)

    def __str__(self):
        return self.title

    @property
    def id(self):  # pylint: disable=invalid-name
       # TODO: hack for compatibility with websauna admin crud, rewrite
        return self.uuid
