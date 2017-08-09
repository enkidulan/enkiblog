# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture()
def tags_crud_tests(dbsession, fakefactory, site, navigator, admin_user):
    from enkiblog.tests.utils import CRUDBasicTest
    return CRUDBasicTest(
        fakefactory.TagFactory, site.admin_menu.tags, navigator, dbsession, admin_user)


def test_create(tags_crud_tests):
    tags_crud_tests.create(
        fields=("title",),
        submit_kw={'status': 'success'}
    )


def test_form_validation(tags_crud_tests, admin_user):
    tags_crud_tests.create(
        user=admin_user,
        fields=(("title", ""),),
        submit_kw={'status': 'validation_error'}
    )


def test_edit(tags_crud_tests):
    tags_crud_tests.edit(
        fields=("title",),
        submit_kw={'status': 'success'}
    )


def test_delete(tags_crud_tests):
    # TODO: add test for checking relations after deleting
    tags_crud_tests.delete()
