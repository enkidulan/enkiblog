""" Workflow configuration and declaration module  """
from pyramid.security import Allow, Everyone, DENY_ALL
from enkiblog.core.workflow import WorkflowBuilder, State, Transition, P, prop


class SimpleWorkflow(WorkflowBuilder):  # pylint: disable=too-few-public-methods
    """ Simple workflow with only public/private states """

    name = 'simple_publication'
    state_attr = 'state'
    description = ''
    permission_checker = None

    permissions = {
        'viewing': ('view',),
        'managing': ('view', 'edit'),
    }

    public = State(
        acl=(P(Allow, (Everyone, ), permissions['viewing']),
             P(Allow, prop('editors'), permissions['managing']),
             P(*DENY_ALL)))
    private = State(
        acl=(P(Allow, prop('editors'), permissions['managing']),
             P(*DENY_ALL)))

    initial_state = private

    publish = Transition(private, public)
    hide = Transition(public, private)

    def is_published(self, context):
        """ checks if context is published and returns bool result """
        # pylint: disable=no-member
        return getattr(context, self.state_attr, None) == self.states.public


def includeme(config):
    """ Pyramids configuration part, initializes workflow and adds request method for it """
    config.registry.workflow = SimpleWorkflow()
    config.add_request_method(lambda r: r.registry.workflow, name='workflow', reify=True)
