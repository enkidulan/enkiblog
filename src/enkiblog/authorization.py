""" Authorization provides """
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.location import lineage
from pyramid.compat import is_nonstr_iter
from pyramid.security import (
    ACLAllowed,
    ACLDenied,
    Allow,
    Deny,
    Everyone,
)


class ContextualACLAuthorizationPolicy(ACLAuthorizationPolicy):
    """ Custom ACLAuthorizationPolicy that passes request """

    def permits(self, context, principals, permission):
        """ same as original ACLAuthorizationPolicy but passes request to acl """

        acl = '<No ACL found on any object in resource lineage>'
        for location in lineage(context):
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            if acl and callable(acl):
                acl = acl(request=context.request)  # that is only modification

            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                if ace_principal in principals:
                    if not is_nonstr_iter(ace_permissions):
                        ace_permissions = [ace_permissions]
                    if permission in ace_permissions:
                        if ace_action == Allow:
                            return ACLAllowed(ace, acl, permission,
                                              principals, location)
                        return ACLDenied(ace, acl, permission,
                                         principals, location)

        return ACLDenied(
            '<default deny>',
            acl,
            permission,
            principals,
            context)

    def principals_allowed_by_permission(self, context, permission):
        """ same as original ACLAuthorizationPolicy but passes request to acl """

        allowed = set()

        for location in reversed(list(lineage(context))):
            # NB: we're walking *up* the object graph from the root
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            allowed_here = set()
            denied_here = set()

            if acl and callable(acl):
                acl = acl(request=context.request)    # that is only modification

            for ace_action, ace_principal, ace_permissions in acl:
                if not is_nonstr_iter(ace_permissions):
                    ace_permissions = [ace_permissions]
                if (ace_action == Allow) and (permission in ace_permissions):
                    if ace_principal not in denied_here:
                        allowed_here.add(ace_principal)
                if (ace_action == Deny) and (permission in ace_permissions):
                    denied_here.add(ace_principal)
                    if ace_principal == Everyone:
                        # clear the entire allowed set, as we've hit a
                        # deny of Everyone ala (Deny, Everyone, ALL)
                        allowed = set()
                        break
                    elif ace_principal in allowed:
                        allowed.remove(ace_principal)

            allowed.update(allowed_here)

        return allowed
