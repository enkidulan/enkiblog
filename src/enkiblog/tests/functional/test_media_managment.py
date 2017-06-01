import pytest


@pytest.fixture()
def media_crud_tests(dbsession, fakefactory, site, navigator, admin_user):
    from enkiblog.tests.utils import CRUDBasicTest
    return CRUDBasicTest(
        fakefactory.MediaFactory, site.admin_menu.media, navigator, dbsession, admin_user)


def test_create(media_crud_tests, fakefactory, dbsession):

    media_crud_tests.create(
        fields=("blob", "description"),
        submit_kw={'status': 'success'}
    )


def test_edit(media_crud_tests, fakefactory, dbsession):

    media_crud_tests.edit(
        fields=("blob", "description"),
        submit_kw={'status': 'success'}
    )


def test_delete(media_crud_tests):
    media_crud_tests.delete()
