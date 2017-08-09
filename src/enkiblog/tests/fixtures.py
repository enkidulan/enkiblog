import pytest


@pytest.fixture()
def fakefactory(base_fakefactory):
    # pylint: disable=redefined-outer-name, unused-argument
    # TODO: Make thread-safe, refactor
    from . import fakefactory
    base_fakefactory.__dict__.update(fakefactory.__dict__)
    return base_fakefactory


@pytest.fixture()
def site(base_site):
    # pylint: disable=redefined-outer-name
    from enkiblog.tests.site import post, media, tag
    site = base_site
    site.add(post.Post)
    site.admin_menu.add(post.PostCRUD().constructor())
    site.admin_menu.add(media.MediaCRUD().constructor())
    site.admin_menu.add(tag.MediaCRUD().constructor())
    return site
