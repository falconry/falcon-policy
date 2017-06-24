import six
from six.moves import UserDict


class PolicyConfig(UserDict):
    @property
    def roles(self):
        return self.data.get('roles', {})

    @property
    def groups(self):
        return self.data.get('groups', {})

    @property
    def routes(self):
        return self.data.get('routes', {})

    @property
    def route_policies(self):
        for route, route_cfg in six.iteritems(self.routes):
            for method, policy in six.iteritems(route_cfg):
                yield route, method, policy
