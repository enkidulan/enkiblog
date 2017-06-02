from enkiblog.tests.site import base
from enkiblog.tests.site import post
from enkiblog.tests.site import media
from enkiblog.tests.site import tag


def site_constructor(url):
    site = base.SiteRoot(url)
    site.add(base.AdminMenu())
    site.add(base.LoginForm())
    site.add(post.Post)
    site.admin_menu.add(post.PostCRUD().constructor())
    site.admin_menu.add(media.MediaCRUD().constructor())
    site.admin_menu.add(tag.MediaCRUD().constructor())
    return site
