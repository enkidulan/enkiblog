import pytest


@pytest.fixture()
def fakefactory(base_fakefactory):
    # TODO: Make thread-safe
    from . import fakefactory
    return fakefactory


@pytest.fixture()
def site(base_site):
    from enkiblog.tests.site import (
        post, media, tag)

    site = base_site
    site.add(post.Post)
    site.admin_menu.add(post.PostCRUD().constructor())
    site.admin_menu.add(media.MediaCRUD().constructor())
    site.admin_menu.add(tag.MediaCRUD().constructor())
    return site
