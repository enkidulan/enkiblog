
class Navigator:
    # make a proper visitor

    def __init__(self, browser, user=None, login_form=None):
        self.browser = browser
        self.user = user
        self.login_form = login_form

    def ensure_user_is_logged_in(self):
        if self.user is None:
            return
        if self.login_form.is_user_loged_in(navigator=self, user=self.user):
            return
        self.login_form.parent.navigate(navigator=self)
        self.login_form.navigate(navigator=self)
        self.login_form.submit(navigator=self, data={'user': self.user})

    def navigate(self, page, check_if_navigated=True, obj=None):
        if self.user:
            self.ensure_user_is_logged_in()
        # pylint: disable=protected-access
        page._navigate(navigator=self, check_if_navigated=check_if_navigated, obj=obj)
        return page

    def submit(self, form, data, status='success', obj=None):
        # TODO: move out?
        # assert form.type == 'form'
        assert isinstance(data, dict)

        form.submit(navigator=self, data=data, obj=obj)
        getattr(form, 'check_' + status)(navigator=self, data=data, obj=obj)

        # if status == 'success':
        #     form.parrent.pages.add()

        return form

    def parse(self, node):
        return node(self.browser)


class Navigatable:

    parent = None

    def is_current_context(self, navigator, obj=None, timeout=None):
        # pylint: disable=unused-argument, no-self-use
        raise NotImplementedError()

    def navigate(self, navigator, obj):
        # pylint: disable=unused-argument, no-self-use
        raise NotImplementedError()

    def _navigate(self, navigator, check_if_navigated=True, obj=None):
        # if self.is_current_context(navigator, timeout=0.1):
        #     return
        if self.parent:
            navigator.navigate(self.parent, check_if_navigated=check_if_navigated, obj=obj)
        self.navigate(navigator, obj=obj)
        if check_if_navigated:
            assert self.is_current_context(navigator, obj=obj)
