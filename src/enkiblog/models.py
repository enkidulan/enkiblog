from uuid import uuid4

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from websauna.system.model.meta import Base
from websauna.system.model.columns import UTCDateTime
from websauna.utils.time import now


class Post(Base):
    __tablename__ = "posts"

    uuid = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)

    created_at = Column(UTCDateTime, default=now, nullable=False)
    published_at = Column(UTCDateTime, default=None, nullable=True)
    updated_at = Column(UTCDateTime, nullable=True, onupdate=now)

    title = Column(String(256), nullable=False)
    description = Column(Text(), nullable=False, default="")

    body = Column(Text(), nullable=False, default="")
    slug = Column(String(256), nullable=False, unique=True)

    state = Column(Text(), nullable=False, default="draft")

    author = Column(String(256), nullable=True)

    @property
    def id(self):
        return self.uuid
