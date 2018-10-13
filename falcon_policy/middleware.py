import falcon

from falcon_policy.config import PolicyConfig
from falcon_policy.policy import PolicyManager


class RoleBasedPolicy(object):
    def __init__(self, config_dict):
        self.config = PolicyConfig(config_dict)
        self.manager = PolicyManager(self.config)

    def process_resource(self, req, resp, resource, params):
        route = req.uri_template

        if isinstance(req.context, dict):
            roles = req.context.get('roles')

        # Assume it's a direct attribute
        else:
            roles = getattr(req.context, 'roles', None)

        # Fallback on the X-Roles Header
        if not roles:
            roles_header = req.get_header('X-Roles', default='@unknown')
            roles = [role.strip() for role in roles_header.split(',')]

        route_policy = self.manager.policies.get(route, {})
        method_policy = route_policy.get(req.method.upper(), [])

        has_role = self.manager.check_roles(roles, method_policy)

        if not has_role:
            raise falcon.HTTPForbidden(
                description='Access to this resource has been restricted'
            )
