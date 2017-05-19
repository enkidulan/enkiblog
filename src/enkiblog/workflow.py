from enkiblog import models
from repoze.workflow import Workflow


def includeme(config):
    # dummy simple singe workflow
    # TODO: workflow is not used anywhere
    workflow = Workflow(
        state_attr='state',
        initial_state='private',
        name='simple_publication',
        permission_checker=None,
    )
    workflow.add_state('public')
    workflow.add_state('private')
    workflow.add_transition('publish', 'private', 'public')
    workflow.add_transition('hide', 'public', 'private')
    workflow.check()
    config.registry.workflow = workflow
