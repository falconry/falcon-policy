import falcon
import pytest
from pretend import stub

from falcon_policy import RoleBasedPolicy


sample_config = {
    'roles': [
        'admin',
        'creator',
        'observer',
        'audit',
    ],
    'groups': {
        'create': ['admin', 'creator'],
        'update': ['admin', 'creator'],
        'read': ['admin', 'creator', 'observer'],
        'delete': ['admin'],
    },
    'routes': {
        '/plainroles': {
            'GET': ['admin'],
            'HEAD': ['@passthrough'],
        },
        '/withgroups': {
            'GET': ['read'],
            'POST': ['create'],
        },
        '/mixed': {
            'GET': ['audit', 'create'],
        },
        '/special-any': {
            'GET': ['@any-role'],
        },
    },
}


def create_req_stub(uri, method, roles_header, context=None,
                    context_type=None):
    return stub(
        uri_template=uri,
        method=method,
        get_header=lambda name, default: roles_header,
        context=context or {},
        context_type=context_type or dict,
    )


def test_failover_to_header():
    middleware = RoleBasedPolicy(sample_config)

    req_stub = create_req_stub('/plainroles', 'head', '@unknown')
    middleware.process_resource(req_stub, None, None, None)


def test_object_context_type():
    middleware = RoleBasedPolicy(sample_config)
    context = stub(roles=['@unknown'])

    req_stub = create_req_stub('/plainroles', 'head', None, context, object)
    middleware.process_resource(req_stub, None, None, None)


def test_passthrough():
    middleware = RoleBasedPolicy(sample_config)

    # Config known route should pass through
    req_stub = create_req_stub(
        '/plainroles',
        'HEAD',
        None,
        {'roles': ['@unknown']}
    )
    middleware.process_resource(req_stub, None, None, None)


def test_unknown_route_should_fail():
    middleware = RoleBasedPolicy(sample_config)
    req_stub = create_req_stub('/unknown', 'put', None, {'roles': ['admin']})

    with pytest.raises(falcon.HTTPForbidden):
        middleware.process_resource(req_stub, None, None, None)


@pytest.mark.parametrize('uri, method, roles', [
    ('/plainroles', 'get', ['admin']),
    ('/withgroups', 'get', ['observer']),
    ('/withgroups', 'get', ['creator', 'observer']),
    ('/withgroups', 'get', ['invalidone', 'observer']),
    ('/mixed', 'get', ['admin']),
    ('/mixed', 'get', ['audit']),
    ('/mixed', 'get', ['creator']),

    # Check the special "@any-role" built-in group
    ('/special-any', 'get', ['admin']),
    ('/special-any', 'get', ['creator']),
    ('/special-any', 'get', ['observer']),
    ('/special-any', 'get', ['audit']),
])
def test_with_valid_role(uri, method, roles):
    middleware = RoleBasedPolicy(sample_config)
    req_stub = create_req_stub(uri, method, None, {'roles': roles})

    # Should not raise an exception
    middleware.process_resource(req_stub, None, None, None)


@pytest.mark.parametrize('uri, method, roles', [
    ('/plainroles', 'get', ['nope']),
    ('/withgroups', 'post', ['observer']),

    # Make sure we can't use the group name
    ('/withgroups', 'post', ['read']),
    ('/withgroups', 'post', ['@any-role']),
    ('/withgroups', 'post', ['@passthrough']),
])
def test_with_invalid_role(uri, method, roles):
    middleware = RoleBasedPolicy(sample_config)
    req_stub = create_req_stub(uri, method, None, {'roles': roles})

    with pytest.raises(falcon.HTTPForbidden):
        middleware.process_resource(req_stub, None, None, None)
