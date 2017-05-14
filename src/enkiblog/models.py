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


class Post(Base):
    __tablename__ = "posts"

    # TODO: move permissions and roles-users out
    permissions = {
        'viewing': ('view',),
        'managing': ('view', 'edit'),  # that looks a bit too much, websauna does it, should I integrate it into websauna? - should admin panel resources use it?
    }

    @property
    def editors(self):
        return (
            self.author,
            'group:admin',
        )

    @property
    def __workflowed_acl__(self):
        # only one workflow allowed for simplicity sake
        return {
            'public': (
                P(Allow, Everyone, self.permissions['viewing']),
                P(Allow, self.editors, self.permissions['managing']),
                P(*DENY_ALL),
            ),
            'draft': (
                P(Allow, self.editors, self.permissions['managing']),
                P(*DENY_ALL),
            ),
        }

    @property
    def __acl__(self):
        acl = self.__workflowed_acl__.get(self.state, (DENY_ALL, ))
        return acl

    @classmethod
    def acl_aware_listing_query(cls, dbsession, effective_principals, actions):
        # !!!: doesn't allow to have localy stored custom acl!!!
        # TODO: make posts objects context factory, move it there
        # import pdb; pdb.set_trace()

        # return dbsession.query(cls).filter_by(state='published')
        # cls.__workflowed_acl__.fget(cls)
        states_and_agents = [(state, perm.agents) for state, perms in cls.__workflowed_acl__.fget(cls).items() for perm in perms if perm.allowance == Allow and not set(perm.actions).isdisjoint(actions)]

        # filtering by effective_principals
        states = [state for (state, agents) in states_and_agents if not set(effective_principals).isdisjoint({agents})] # TODO: add support for itterable agents
        query = dbsession.query(cls).filter(cls.state.in_(states))

        # filtering by relations - owner, group member, etc...
        # states = [state for (state, agents) in states_and_agents if isinstance(agents, sa.Column) and state not in states]


        # states_and_agents
        return query

    uuid = sa.Column(psql_dialect.UUID(as_uuid=True), default=uuid4, primary_key=True)

    created_at = sa.Column(UTCDateTime, default=now, nullable=False)
    published_at = sa.Column(UTCDateTime, default=None, nullable=True)
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    title = sa.Column(sa.String(256), nullable=False)
    description = sa.Column(sa.Text(), nullable=False, default="")

    body = sa.Column(sa.Text(), nullable=False, default="")
    slug = sa.Column(sa.String(256), nullable=False, unique=True)

    # TODO: move all workflow related to json
    #       sa.Column(NestedMutationDict.as_mutable(psql.JSONB), default=dict)
    state = sa.Column(sa.Text(), nullable=False, default="private")

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    author = sa.orm.relationship('User')

    @property
    def id(self):  # XXX:
        return self.uuid

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

    state = sa.Column(sa.Text(), nullable=False, default="draft")

    author = sa.Column(sa.String(256), nullable=True)

    @property
    def id(self):  # XXX:
        return self.uuid
