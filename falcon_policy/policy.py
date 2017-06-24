import collections
import itertools


class PolicyManager(object):
    def __init__(self, config):
        self.config = config
        self.policies = collections.defaultdict(dict)

        self.cache_expanded_policies()

    def expand_policy(self, policy):
        to_expand = [
            item for item in policy
            if item in self.config.groups
        ]

        group_roles = itertools.chain.from_iterable([
            self.config.groups[item] for item in to_expand
        ])

        roles = set(policy) - set(to_expand)
        authorized_roles = roles.union(set(group_roles))

        return authorized_roles

    def cache_expanded_policies(self):
        for route, method, policy in self.config.route_policies:
            self.policies[route][method.upper()] = self.expand_policy(policy)

    def check_roles(self, provided_roles, policy):
        authorized_list = policy

        if '@any-role' in policy:
            authorized_list = self.config.roles

        elif '@passthrough' in policy:
            return next(iter(provided_roles))

        for provided in provided_roles:
            role = provided.strip()

            if role in authorized_list:
                return role
