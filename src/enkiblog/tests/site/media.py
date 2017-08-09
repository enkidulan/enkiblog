from enkiblog.core.testing.site import CRUD


class MediaCRUD(CRUD):
    # pylint: disable=no-self-use, abstract-method

    listing_page_name = 'media'
    entity_plural = 'media'
    entity_single = 'media'

    def submit_add_form(self, browser, data):
        browser.fill("description", data['description'])
        browser.find_by_name("upload")[0].value = data['blob'].decode('utf-8')

    def check_success_add_form(self, browser, data, check_success_message):
        # After login we see a profile link to our profile
        assert browser.is_text_present(data['description'])
        assert browser.is_text_present(data['title'])
        # TODO: add check that all submitted fields were checked here
