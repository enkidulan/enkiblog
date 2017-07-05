from repoze.workflow import Workflow
from pyramid.security import Allow
from collections import namedtuple
from inspect import signature
from functools import partial


P = namedtuple('Permission', ('allowance', 'agents', 'actions'))


def prop(prop):
    def getter(instance):
        return getattr(instance, prop)
    return getter


class PropsProxy:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class State(PropsProxy):
    pass


class Transition(PropsProxy):
    pass


class WorkflowBuilder:
    __baseclass = Workflow

    def __new__(cls):
        init_params = {n: getattr(cls, n) for n in signature(cls.__baseclass).parameters}
        states = {n: a for n, a in cls.__dict__.items() if isinstance(a, State)}
        transitions = {n: a for n, a in cls.__dict__.items() if isinstance(a, Transition)}
        members = {
            n: a for n, a in cls.__dict__.items()
            if not(n.startswith('_') or n in [*init_params, *states, *transitions])}
        members['states'] = type(cls.__name__ + 'States', (object, ), {i: i for i in states})
        reverse_states = {v: k for k, v in states.items()}
        init_params['initial_state'] = reverse_states[init_params['initial_state']]

        workflow_cls = type(cls.__name__, (cls.__baseclass, ), members)

        workflow = workflow_cls(**init_params)

        for name, attr in states.items():
            workflow.add_state(name, *attr.args, **attr.kwargs)

        for name, attr in transitions.items():
            args = [reverse_states[i] if isinstance(i, State) else i for i in attr.args]
            kwargs = {k: reverse_states[v] if isinstance(v, State) else v for k, v in attr.kwargs.items()}
            workflow.add_transition(name, *args, **kwargs)

        workflow.check()
        return workflow


def resolve_props(context, permission, deepth=2):
    agents = permission.agents
    for i in range(deepth):
        if not callable(agents):
            break
        agents = agents(context)
    else:
        raise RuntimeError("Could not resolve '%s' callable property " % permission.agents)
    return P(permission.allowance, agents, permission.actions)


def get_allowance_permissions_per_state(context, request):
    workflow = request.workflow
    resolwer = partial(resolve_props, context)
    for state in workflow.state_info(context, request):
        for permission in map(resolwer, state['data']['acl']):
            if permission.allowance != Allow:
                continue
            yield state['name'], permission
