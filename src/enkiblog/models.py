from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql_dialect
# from sqlalchemy.orm import relationship

from websauna.system.model.meta import Base
from websauna.system.model.columns import UTCDateTime
from websauna.utils.time import now


class Post(Base):
    __tablename__ = "posts"

    uuid = sa.Column(psql_dialect.UUID(as_uuid=True), default=uuid4, primary_key=True)

    created_at = sa.Column(UTCDateTime, default=now, nullable=False)
    published_at = sa.Column(UTCDateTime, default=None, nullable=True)
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    title = sa.Column(sa.String(256), nullable=False)
    description = sa.Column(sa.Text(), nullable=False, default="")

    body = sa.Column(sa.Text(), nullable=False, default="")
    slug = sa.Column(sa.String(256), nullable=False, unique=True)

    state = sa.Column(sa.Text(), nullable=False, default="draft")

    author = sa.Column(sa.String(256), nullable=True)

    @property
    def id(self):
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

    state = sa.Column(sa.Text(), nullable=False, default="draft")

    author = sa.Column(sa.String(256), nullable=True)

    @property
    def id(self):
        return self.uuid
