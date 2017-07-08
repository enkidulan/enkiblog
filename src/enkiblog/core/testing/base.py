from functools import partial
from uuid import uuid4
import transaction


def get_key_and_value(obj, value, getter=None):
    if isinstance(value, str):
        getter = getter if getter else getattr
        return value, getter(obj, value)
    return value


class CRUDBasicTest:

    def __init__(self, obj_factory, listing_page, navigator, dbsession, admin_user):
        self.navigator = navigator
        self.listing_page = listing_page
        self.obj_factory = obj_factory
        self.dbsession = dbsession
        self.admin_user = admin_user

    def create(self, fields, submit_kw, user=None):
        user = user if user else self.admin_user
        navigator = self.navigator(user=user)
        obj = self.obj_factory.build()
        navigator.submit(
            self.listing_page.add_page.add_form,
            data=dict(map(partial(get_key_and_value, obj), fields)),
            **submit_kw)
        return obj

    def delete(self, user=None):
        user = user if user else self.admin_user

        with transaction.manager:
            self.obj_factory()

        navigator = self.navigator(user=user)
        navigator.navigate(self.listing_page)

        assert navigator.browser.is_text_present("Total 1 item")

        navigator.browser.find_by_css('.btn-crud-listing-delete').click()
        assert navigator.browser.is_text_present("Confirm delete")

        navigator.browser.find_by_css('#btn-delete-yes').click()
        assert navigator.browser.is_text_present("Deleted")

        navigator.navigate(self.listing_page)
        assert navigator.browser.is_text_present("No items")

    def edit(self, submit_kw, fields, user=None):
        user = user if user else self.admin_user

        with transaction.manager:
            obj = self.obj_factory()
            self.dbsession.expunge_all()

        navigator = self.navigator(user=user)

        data = dict(map(partial(get_key_and_value, obj, getter=lambda x, y: uuid4().hex), fields))

        navigator.submit(
            self.listing_page.edit_page.edit_form,
            obj=obj,
            data=data,
            **submit_kw)
