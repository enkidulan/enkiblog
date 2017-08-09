from itertools import chain

import transaction
from testfixtures import compare as _base_compare

# TODO: move to integrational tests?


def compare(a, b):  # pylint: disable=invalid-name
    _base_compare(sorted(repr(i) for i in a), sorted(repr(i) for i in b))


def test_public_state_listing(fakefactory, dbsession, request):
    # pylint: disable=too-many-locals

    from enkiblog.models import Post
    from enkiblog.workflow import get_worflow

    with transaction.manager:
        user = fakefactory.UserFactory()

        user_public_posts = fakefactory.PostFactory.create_batch(3, author=user, state='public')

        # noise objects
        user_private_posts = fakefactory.PostFactory.create_batch(3, author=user, state='private')
        second_user_private_posts = fakefactory.PostFactory.create_batch(
            3, author=fakefactory.UserFactory(), state='private')

        dbsession.expunge_all()

    def get_posts(effective_principals, actions, user):
        request.effective_principals = effective_principals
        request.user = user
        request.registry = request
        request.workflow = get_worflow(request)
        return dbsession.query(Post).acl_filter(request, actions=actions)
        # return Post.acl_aware_listing_query(
        #      dbsession, effective_principals, actions, user=user).all()

    def get_posts_for_managing(*effective_principals, user=None):
        return get_posts(effective_principals=effective_principals, actions=['edit'], user=user)

    def get_posts_for_viewing(*effective_principals, user=None):
        return get_posts(effective_principals=effective_principals, actions=['view'], user=user)

    unpriveleged_view_posts = get_posts_for_viewing('system.Everyone')
    compare(unpriveleged_view_posts, user_public_posts)

    unpriveleged_manage_posts = get_posts_for_managing('system.Everyone')
    compare(unpriveleged_manage_posts, [])

    author_view_posts = get_posts_for_viewing('system.Everyone', user.uuid, user=user)
    compare(author_view_posts, chain(user_public_posts, user_private_posts))

    author_manage_posts = get_posts_for_managing('system.Everyone', user.uuid, user=user)
    compare(author_manage_posts, chain(user_public_posts, user_private_posts))

    admin_view_posts = get_posts_for_viewing('system.Everyone', 'group:admin')
    compare(admin_view_posts, chain(
        user_public_posts, user_private_posts, second_user_private_posts))

    admin_manage_posts = get_posts_for_managing('system.Everyone', 'group:admin')
    compare(admin_manage_posts, chain(
        user_public_posts, user_private_posts, second_user_private_posts))
