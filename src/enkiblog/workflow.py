from repoze.workflow import Workflow
from pyramid.security import Allow, Everyone, DENY_ALL
from collections import namedtuple

P = namedtuple('Permission', ('allowance', 'agents', 'actions'))


def prop(prop):
    def getter(instance):
        return getattr(instance, prop)
    return getter


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
        acl=(P(Allow, (Everyone, ), permissions['viewing']),
             P(Allow, prop('editors'), permissions['managing']),
             P(*DENY_ALL))
    )
    workflow.add_state(
        'private',
        acl=(P(Allow, prop('editors'), permissions['managing']),
             P(*DENY_ALL))
    )
    workflow.add_transition('publish', 'private', 'public')
    workflow.add_transition('hide', 'public', 'private')
    workflow.check()
    return workflow


def get_worflow(requst):
    workflow = getattr(requst.registry, "workflow", None)
    if workflow is None:
        workflow = requst.registry.workflow = simple_workflow()
    return workflow


def includeme(config):
    config.add_request_method(get_worflow, name='workflow', reify=True)
