"""
Database meta module, this mainly to set custom query class for
alchemy DB session. Reason is to provide `acl_filter` method that
plays along with workfolw and acl to provide authorization control for
sets of records.
"""
from sqlalchemy.orm import Query
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa

InstrumentedAttribute = sa.orm.attributes.InstrumentedAttribute


def get_principales_states(allowance_per_state, actions):
    """ Returns allowing principals for both relational and users effective_principals """
    allowing_states_and_agents = [
        (state, perm.agents)
        for state, perm in allowance_per_state
        if not set(perm.actions).isdisjoint(actions)
    ]

    relational_states = []
    principale_states = []
    for (state, agents) in allowing_states_and_agents:
        for agent in agents:
            storage = (
                relational_states
                if isinstance(agent, InstrumentedAttribute) else
                principale_states)
            storage.append((state, agent))
    return relational_states, principale_states


def acl_query_params_builder(cls, request, actions):
    """ Returns arguments for a filter that would assure authorization control """
    effective_principals = set(request.effective_principals)
    user = request.user

    # Note: currently doesn't allow to have locally stored custom acl
    allowance_per_state = request.workflow.get_allowance_permissions(cls, request)
    relational_states, principale_states = get_principales_states(
        allowance_per_state, actions)

    allowing_states_for_principals = tuple(
        state for (state, agent) in principale_states
        if agent in effective_principals
    )

    params = cls.state.in_(allowing_states_for_principals)
    if user:
        acl_allowed_posts_queries = [
            sa.and_(cls.state == state, agent == user)
            for (state, agent) in relational_states]
        params = sa.or_(params, *acl_allowed_posts_queries)
    return params


class ACLFilteringQuery(Query):

    """ Query class that provides authorization abilities """

    def acl_filter(self, request, actions=('view',)):
        """
        Applies acl-workflow based filtering to query entities to achieve
        authorization on a query level
        """
        query = self
        for entity in self._entities:
            params = acl_query_params_builder(entity.mapper.class_, request, actions)
            query = query.filter(params)
        return query


def create_session_maker(engine):
    """ Custom session maker that sets query class for session  """
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine, query_cls=ACLFilteringQuery)
    return dbmaker
