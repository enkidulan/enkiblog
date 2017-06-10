from repoze.workflow import Workflow
from pyramid.security import Allow, Everyone, Deny, DENY_ALL
from collections import namedtuple
import sqlalchemy as sa
from functools import partial


P = namedtuple('Permission', ('allowance', 'agents', 'actions'))


def prop(prop):
    def getter(instance):
        return getattr(instance, prop)
    return getter


def acl_query(cls, dbsession, effective_principals, actions, user=None):
    # TODO: add tests (or is it added ?)
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


def simple_workflow():
    workflow = Workflow(
        state_attr='state',
        initial_state='private',
        name='simple_publication',
        permission_checker=None,
    )
    permissions = {
        'viewing': ('view',),
        'managing': ('view', 'edit'),  # that looks a bit too much, websauna does it, should I integrate it into websauna? - should admin panel resources use it?
    }
    workflow.add_state(
        'public',
        acl_query=acl_query,
        acl=(P(Allow, (Everyone, ), permissions['viewing']),
             P(Allow, prop('editors'), permissions['managing']),
             P(*DENY_ALL))
    )
    workflow.add_state(
        'private',
        acl_query=acl_query,
        acl=(P(Allow, prop('editors'), permissions['managing']),
             P(*DENY_ALL))
    )
    workflow.add_transition('publish', 'private', 'public')
    workflow.add_transition('hide', 'public', 'private')
    workflow.check()
    return workflow


def includeme(config):
    # dummy simple singe workflow
    # TODO: workflow is not used anywhere

    workflow = simple_workflow()

    # XXX: replace with mix of pyramid_services for using utility for IWorkflow
    config.registry.workflow = workflow  # is it right? remove it, use proper register!!!
    config.add_request_method(workflow, name='workflow', reify=True)


def acl_helper(context, request, as_a_query=False):
    # workflow = get_workflow(self, IWorkflow)
    workflow = request.workflow
    if not workflow.has_state(context):
        workflow.initialize(context)
    for state in workflow.state_info(context, request):
        if state['current']:
            break

    if not as_a_query:
        raise
        # handle prop option
        return state['data']['acl']

    query_builder = state['data']['acl_query']
    query = query_builder(
        cls=context,
        dbsession=request.dbsession,
        effective_principals=request.effective_principals,
        actions=('view', ),  # XXX:
        # actions=request.actions,
        user=request.user)
    return query


class ACLMixin:

    @classmethod
    def __acl__(self, request=None):
        return acl_helper(self, request, as_a_query=False)

    @classmethod
    def acl_query(self, request=None):
        return acl_helper(self, request, as_a_query=True)
