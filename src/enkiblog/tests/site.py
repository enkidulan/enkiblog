import re
from enkiblog.tests.navigator import Navigatable


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class SiteNode(Navigatable):

    def __init__(self):
        self.nodes = {}
        self.name = convert(self.__class__.__name__)  # TODO: rename

    def add(self, node):
        assert node.name not in self.nodes  # for having explicit ovverinding
        self.nodes[node.name] = node
        node.parent = self
        setattr(self, node.name, node)


class SiteRoot(SiteNode):

    def __init__(self, url):
        super().__init__()
        self.url = url

    def is_current_context(self, navigator, timeout=None):
        return navigator.browser.url.startswith(self.url)
        # return navigator.browser.url.strip('/') == self.url.strip('/')

    def navigate(self, navigator):
        navigator.browser.visit(self.url)


class AdminMenu(SiteNode):

    def is_current_context(self, navigator, timeout=None):
        return navigator.browser.is_element_present_by_css("#admin-main", wait_time=timeout)

    def navigate(self, navigator):
        navigator.browser.find_by_css("#nav-admin").click()


class Posts(SiteNode):  # duplicates AdminMenu for simlicity sake

    def is_current_context(self, navigator, timeout=None):
        return navigator.browser.is_text_present("All posts", wait_time=timeout)

    def navigate(self, navigator):
        navigator.browser.find_by_css('#btn-panel-list-posts').click()


class Post:
    name = 'post'

    title = None
    slug = None

    def __init__(self, browser):
        self.title = browser.find_by_css('#post-title').text
        self.slug = browser.url.rsplit('/', 1)[1]


class AddPostPage(SiteNode):

    def is_current_context(self, navigator, timeout=None):
        return navigator.browser.is_text_present("Add new post", wait_time=timeout)

    def navigate(self, navigator):
        navigator.browser.find_by_css("#btn-crud-add").click()


class AddPostForm(SiteNode):

    def is_current_context(self, navigator, timeout=None):
        return navigator.browser.is_text_present("Add new post", wait_time=timeout)

    def navigate(self, navigator):
        pass

    def submit(self, navigator, data):

        navigator.navigate(self)

        navigator.browser.fill("title", data['title'])
        navigator.browser.fill("descriptions", data['descriptions'])
        navigator.browser.fill("body", data['body'])

        navigator.browser.find_by_name("add").click()

    def check_success(self, navigator, data):

        # After login we see a profile link to our profile
        assert navigator.browser.is_text_present("Item added")
        assert navigator.browser.is_text_present(data['title'])

    def check_validation_error(self, navigator, data):
        assert navigator.browser.is_text_present("There was a problem with your submission")


class LoginForm(SiteNode):

    def is_current_context(self, navigator, timeout=None):
        return navigator.browser.is_element_present_by_css("#login-form", wait_time=timeout)

    def navigate(self, navigator):
        navigator.browser.find_by_css("#nav-sign-in").click()

    def submit(self, navigator, data):

        user = data['user']
        navigator.browser.fill("username", user.email)
        navigator.browser.fill("password", user._fb_excluded.password)
        navigator.browser.find_by_name("login_email").click()

        assert self.is_user_loged_in(navigator, user)

    def is_user_loged_in(self, navigator, user):
        return navigator.browser.is_element_present_by_css("#nav-logout")


def site_constructor(url):
    site = SiteRoot(url)
    site.add(AdminMenu())
    site.add(LoginForm())
    site.add(Post)
    site.admin_menu.add(Posts())
    site.admin_menu.posts.add(AddPostPage())
    site.admin_menu.posts.add_post_page.add(AddPostForm())
    return site
