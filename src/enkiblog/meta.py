from functools import partial
from sqlalchemy.orm import Query
from sqlalchemy.orm import sessionmaker
from enkiblog.workflow import P, Allow
import sqlalchemy as sa
InstrumentedAttribute = sa.orm.attributes.InstrumentedAttribute


def resolve_callable_props(context, permission):

    agents = permission.agents
    for i in range(10):
        if not callable(agents):
            break
        agents = agents(context)
    else:
        raise RuntimeError("Could not resolve '%s' callable property " % permission.agents)

    return P(permission.allowance, agents, permission.actions)


def get_allowance_permissions_per_state(context, request):
    workflow = request.workflow
    resolwer = partial(resolve_callable_props, context)
    for state in workflow.state_info(context, request):
        for permission in map(resolwer, state['data']['acl']):
            if permission.allowance != Allow:
                continue
            yield state['name'], permission


def get_relational_and_principale_states(allowance_per_state, actions):
    allowing_states_and_agents = [
        (state, perm.agents)
        for state, perm in allowance_per_state
        if not set(perm.actions).isdisjoint(actions)
    ]

    relational_states = []
    principale_states = []
    for (state, agents) in allowing_states_and_agents:
        for agent in agents:
            (relational_states
             if isinstance(agent, InstrumentedAttribute) else
             principale_states
             ).append((state, agent))
    return relational_states, principale_states


def acl_query_params_builder(cls, request, actions):
    effective_principals = set(request.effective_principals)
    user = request.user
    # TODO: add tests (or is it added ?)
    # !!!: doesn't allow to have localy stored custom acl!!!

    allowance_per_state = get_allowance_permissions_per_state(cls, request)
    relational_states, principale_states = get_relational_and_principale_states(
        allowance_per_state, actions)

    allowing_states_for_principals = tuple(
        state for (state, agent) in principale_states
        if agent in effective_principals
    )

    # params = cls.state.in_(allowing_states_for_principals)
    params = sa.or_(cls.state == state for state in allowing_states_for_principals)
    if user:
        acl_allowed_posts_queries = [
            sa.and_(cls.state == state, agent == user)
            for (state, agent) in relational_states]
        params = sa.or_(params, *acl_allowed_posts_queries)
    return params


class ACLFilteringQuery(Query):

    def acl_filter(self, request, actions=('view',)):
        query = self
        for entity in self._entities:
            params = acl_query_params_builder(entity.type, request, actions)
            query = query.filter(params)
        return query


def create_session_maker(engine):
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine, query_cls=ACLFilteringQuery)
    return dbmaker
