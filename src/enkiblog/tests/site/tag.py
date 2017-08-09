# pylint: disable=no-self-use, abstract-method, too-few-public-methods
from enkiblog.core.testing.site import CRUD


class MediaCRUD(CRUD):

    listing_page_name = 'tags'
    entity_plural = 'tags'
    entity_single = 'tag'

    def submit_add_form(self, browser, data):
        browser.fill("title", data['title'])

    def check_success_add_form(self, browser, data, check_success_message):
        assert browser.is_text_present(data['title'])
