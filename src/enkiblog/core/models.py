from uuid import uuid4
from functools import partial

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql_dialect
from sqlalchemy.ext.declarative import declared_attr

from websauna.system.model.columns import UTCDateTime
from websauna.utils.time import now


UUID = partial(psql_dialect.UUID, as_uuid=True)


class WorflowMixin:

    # IDEA: attach state directly from workflow on attach_model_to_base step
    @declared_attr
    def state(cls):  # pylint: disable=missing-docstring
        registry = cls.metadata.pyramid_config.registry
        default_state = registry.workflow.initial_state
        return sa.Column(sa.Text(), nullable=False, default=default_state, index=True)


class BaseResourceMixin:

    uuid = sa.Column(UUID(), default=uuid4, primary_key=True)
    slug = sa.Column(sa.String(256), nullable=False, unique=True)
    title = sa.Column(sa.String(256), unique=True, nullable=False)

    def __repr__(self):
        return "#{}: {}".format(self.uuid, self.title)

    def __str__(self):
        return self.title


class ContentResourceMixin(BaseResourceMixin, WorflowMixin):

    created_at = sa.Column(UTCDateTime, default=now, nullable=False)
    published_at = sa.Column(UTCDateTime, default=None, nullable=True, index=True, unique=True)
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    description = sa.Column(sa.Text(), nullable=False, default="")

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    author = sa.orm.relationship('User')

    def editors(self):
        """
        Returns list of post editors, returned items may be pyramid effective
        principles or model fields
        """
        return (
            self.author,
            'group:admin',
        )

    @declared_attr
    def ensure_publication_date(cls):  # pylint: disable=missing-docstring
        workflow = cls.metadata.pyramid_config.registry.registry
        return sa.CheckConstraint(
            "state != '%s' OR (state = '%s' AND published_at IS NOT NULL)" % (
                workflow.states.public, workflow.states.public))
