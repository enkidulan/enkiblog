import transaction
import pytest


@pytest.fixture()
def post_crud_tests(dbsession, fakefactory, site, navigator, admin_user):
    from enkiblog.tests.utils import CRUDBasicTest
    return CRUDBasicTest(
        fakefactory.PostFactory, site.admin_menu.posts, navigator, dbsession, admin_user)


def test_create(post_crud_tests, fakefactory, dbsession):

    with transaction.manager:
        tags = fakefactory.TagFactory.create_batch(size=4)
        dbsession.expunge_all()

    post_crud_tests.create(
        fields=(
            "title",
            ("tags", [i.title for i in tags]),
            "description",
            "body"),
        submit_kw={'status': 'success'}
    )


def test_form_validation(post_crud_tests, admin_user):
    post_crud_tests.create(
        user=admin_user,
        fields=(
            ("title", ""),
            "description",
            "body"),
        submit_kw={'status': 'validation_error'}
    )


def test_edit(post_crud_tests, fakefactory, dbsession):

    with transaction.manager:
        tags = fakefactory.TagFactory.create_batch(size=4)
        dbsession.expunge_all()

    post_crud_tests.edit(
        fields=(
            "title",
            "description",
            ("tags", [i.title for i in tags]),
            "body"),
        submit_kw={'status': 'success'}
    )


def test_delete(post_crud_tests):
    post_crud_tests.delete()
