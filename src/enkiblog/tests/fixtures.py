import pytest
from functools import partial
import transaction

from enkiblog.tests.navigator import Navigator
from enkiblog.tests.site import site_constructor


@pytest.fixture()
def fakefactory(dbsession):
    # TODO: Make thread-safe
    from . import fakefactory
    fakefactory.db_session_proxy.session = dbsession
    try:
        yield fakefactory
    finally:
        fakefactory.db_session_proxy.session = None


@pytest.fixture()
def admin_user(fakefactory, dbsession):
    with transaction.manager:
        user = fakefactory.AdminFactory()
        dbsession.expunge_all()
    return user


@pytest.fixture()
def navigator(browser, site):
    return partial(
        Navigator,
        browser=browser,
        login_form=getattr(site, 'login_form', None)
    )


@pytest.fixture()
def site(web_server):
    return site_constructor(web_server)
