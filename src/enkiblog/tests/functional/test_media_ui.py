# pylint: disable=invalid-name
import transaction
from enkiblog.tests import fakefactory as module_fakefactory


def test_media_is_accesible_by_url(
        browser, web_server, fakefactory, dbsession):

    with transaction.manager:
        obj = fakefactory.MediaFactory(state='public')
        dbsession.expunge_all()

    browser.visit(web_server + '/media/' + obj.slug)
    # NOTE: dummy but based on faker content generation
    assert browser.is_text_present(module_fakefactory.__file__)
    assert browser.url.endswith('/media/' + obj.slug)


def test_user_doesnt_see_not_published_media(
        web_server, browser, fakefactory, dbsession):

    with transaction.manager:
        obj = fakefactory.MediaFactory()
        dbsession.expunge_all()
    # XXX: redesign url making func, currently is inflexible
    browser.visit(web_server + '/programming/' + obj.slug)
    assert browser.is_text_present('Not found')
