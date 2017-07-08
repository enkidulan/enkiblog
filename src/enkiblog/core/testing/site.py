import re
from enkiblog.tests.navigator import Navigatable


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class SiteNode(Navigatable):
    name = None
    nodes = None

    def __init__(self):
        self.nodes = {}
        self.name = self.name if self.name else convert(self.__class__.__name__)  # TODO: rename

    def add(self, node):
        assert node.name not in self.nodes  # for having explicit ovverinding
        self.nodes[node.name] = node
        node.parent = self
        setattr(self, node.name, node)


class SiteRoot(SiteNode):

    def __init__(self, url):
        super().__init__()
        self.url = url

    def is_current_context(self, navigator, obj=None, timeout=None):
        return navigator.browser.url.startswith(self.url)
        # return navigator.browser.url.strip('/') == self.url.strip('/')

    def navigate(self, navigator, obj=None):
        navigator.browser.visit(self.url)


class AdminMenu(SiteNode):

    def is_current_context(self, navigator, timeout=None, obj=None):
        return navigator.browser.is_element_present_by_css("#admin-main", wait_time=timeout)

    def navigate(self, navigator, obj=None):
        navigator.browser.find_by_css("#nav-admin").click()


class LoginForm(SiteNode):

    def is_current_context(self, navigator, timeout=None, obj=None):
        return navigator.browser.is_element_present_by_css("#login-form", wait_time=timeout)

    def navigate(self, navigator, obj=None):
        navigator.browser.find_by_css("#nav-sign-in").click()

    def submit(self, navigator, data, obj=None):

        user = data['user']
        navigator.browser.fill("username", user.email)
        navigator.browser.fill("password", user._fb_excluded.password)
        navigator.browser.find_by_name("login_email").click()

        assert self.is_user_loged_in(navigator, user)

    def is_user_loged_in(self, navigator, user):
        return navigator.browser.is_element_present_by_css("#nav-logout")


class CRUDSiteNode(SiteNode):

    def __init__(self, crud_base):
        super().__init__()
        self.crud_base = crud_base
        self.name = getattr(self.crud_base, self.name + '_name', self.name)
        self.plural = self.crud_base.entity_plural
        self.single = self.crud_base.entity_single


class CRUD:

    listing_page_name = None
    entity_plural = None
    entity_single = None

    def submit_add_form_form(self, browser, data):
        raise NotImplementedError()

    def check_success_add_form(self, browser, data, check_success_message):
        raise NotImplementedError()

    class ListingPage(CRUDSiteNode):  # duplicates AdminMenu for simlicity sake

        def is_current_context(self, navigator, timeout=None, obj=None):
            return navigator.browser.is_text_present("All %s" % self.plural, wait_time=timeout)

        def navigate(self, navigator, obj=None):
            navigator.browser.find_by_css('#btn-panel-list-%s' % self.plural).click()

    class AddPage(CRUDSiteNode):

        def is_current_context(self, navigator, timeout=None, obj=None):
            return navigator.browser.is_text_present("Add new %s" % self.single, wait_time=timeout)

        def navigate(self, navigator, obj=None):
            navigator.browser.find_by_css("#btn-crud-add").click()

    class EditPage(CRUDSiteNode):

        # TODO: rename method
        def is_current_context(self, navigator, timeout=None, obj=None):
            return navigator.browser.is_text_present("Editing #%s" % obj.title, wait_time=timeout)

        def navigate(self, navigator, obj=None):
            navigator.browser.find_by_css(".crud-row-%s .btn-crud-listing-edit" % obj.uuid).click()

    class AddForm(CRUDSiteNode):

        check_success_message = "Item added"

        def is_current_context(self, navigator, timeout=None, obj=None):
            return navigator.browser.is_text_present("Add new %s" % self.single, wait_time=timeout)

        def navigate(self, navigator, obj=None):
            pass

        def submit(self, navigator, data, obj=None):

            navigator.navigate(self, obj=obj)

            self.crud_base.submit_add_form(navigator.browser, data)

            self.submit_form(navigator)

        def submit_form(self, navigator):  # TODO: naming is not good at all
            navigator.browser.find_by_name("add").click()

        def check_success(self, navigator, data, obj=None):

            self.crud_base.check_success_add_form(navigator.browser, data, self.check_success_message)

        def check_validation_error(self, navigator, data, obj=None):
            assert navigator.browser.is_text_present("There was a problem with your submission")

    class EditForm(AddForm):
        check_success_message = "Changes saved"

        def is_current_context(self, navigator, timeout=None, obj=None):
            return navigator.browser.is_text_present("Editing #%s" % obj.title, wait_time=timeout)

        def submit_form(self, navigator):  # TODO: naming is not good at all
            navigator.browser.find_by_name("save").click()

    def constructor(self):
        crud_listing = self.ListingPage(crud_base=self)
        crud_listing.add(self.AddPage(crud_base=self))
        crud_listing.add_page.add(self.AddForm(crud_base=self))
        crud_listing.add(self.EditPage(crud_base=self))
        crud_listing.edit_page.add(self.EditForm(crud_base=self))
        return crud_listing
