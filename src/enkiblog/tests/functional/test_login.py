"""An example login test case."""

import transaction


def test_login(browser, navigator, site, dbsession, fakefactory):

    with transaction.manager:
        user = fakefactory.UserFactory()
        dbsession.expunge_all()

    navigator = navigator(user=user)
    navigator.navigate(site)
    assert browser.is_element_present_by_css("#nav-logout")
