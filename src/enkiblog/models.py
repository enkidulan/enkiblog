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
        # NOTE: only one workflow allowed for simplicity sake
        # NOTE: acl agents and actions is always tuples
        return {
            'public': (
                P(Allow, (Everyone, ), self.permissions['viewing']),
                P(Allow, self.editors, self.permissions['managing']),
                P(*DENY_ALL),
            ),
            'private': (
                P(Allow, self.editors, self.permissions['managing']),
                P(*DENY_ALL),
            ),
        }

    @property
    def __acl__(self):
        acl = self.__workflowed_acl__.get(self.state, (DENY_ALL, ))
        return acl

    @classmethod
    def acl_aware_listing_query(cls, dbsession, effective_principals, actions, user=None):
        # TODO: take user from effective_principals
        # !!!: doesn't allow to have localy stored custom acl!!!
        # TODO: make posts objects context factory, move it there
        # import pdb; pdb.set_trace()

        # return dbsession.query(cls).filter_by(state='published')
        # cls.__workflowed_acl__.fget(cls)
        allowing_states_and_agents = [
            (state, perm.agents if isinstance(perm.agents, tuple) else perm.agents.fget(cls))
            for state, perms in cls.__workflowed_acl__.fget(cls).items()
            for perm in perms
            if perm.allowance == Allow
            and not set(perm.actions).isdisjoint(actions)
        ]

        relational_states = [
            (state, agent) for (state, agents) in allowing_states_and_agents
            for agent in agents if isinstance(agent, sa.orm.attributes.InstrumentedAttribute)]

        principale_states = [(state, agents) for (state, agents) in allowing_states_and_agents]

        # filtering by general effective_principals
        allowing_states_for_principals = [
            state for (state, agent) in principale_states
            if not set(effective_principals).isdisjoint(agent)
        ]  # TODO: add support for itterable agents
        query = dbsession.query(cls).filter(cls.state.in_(allowing_states_for_principals))

        if user:
            acl_allowed_posts_queries = [
                dbsession.query(cls).filter(cls.state == state).filter(agent == user)
                for (state, agent) in relational_states]
            query = query.union(*acl_allowed_posts_queries)  # TODO add .distinct(cls.uuid) add distinct

        return query

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
    state = sa.Column(sa.Text(), nullable=False, default="private", index=True)

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    author = sa.orm.relationship('User')

    tags = sa.orm.relationship(
        'Tag', secondary=AssociationPostsTags.__tablename__, back_populates="posts")

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

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    author = sa.orm.relationship('User')

    @property
    def id(self):  # XXX:
        return self.uuid


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
