from functools import partial

import pytest
import transaction

from enkiblog.core.testing.navigator import Navigator
from enkiblog.core.testing.site import site_constructor


@pytest.fixture()
def base_fakefactory(dbsession):
    # TODO: Make thread-safe
    from enkiblog.core.testing import fakefactory
    fakefactory.DB_SESSION_PROXY.session = dbsession
    try:
        yield fakefactory
    finally:
        fakefactory.DB_SESSION_PROXY.session = None


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
def base_site(web_server):
    return site_constructor(web_server)
