# pylint: disable=no-self-use, abstract-method, too-few-public-methods
from enkiblog.core.testing.site import CRUD


class Post:
    name = 'post'

    title = None
    slug = None

    def __init__(self, browser):
        self.title = browser.find_by_css('#post-title').text
        self.slug = browser.url.rsplit('/', 1)[1]


class PostCRUD(CRUD):

    listing_page_name = 'posts'
    entity_plural = 'posts'
    entity_single = 'post'

    def submit_add_form(self, browser, data):
        browser.fill("title", data['title'])
        browser.fill("description", data['description'])
        # adding tags
        tags_input = browser.find_by_xpath(
            '//select[@name="tags"]/following::input[@type="search"]')[0]
        for tag in data.get('tags', []):
            tags_input.type(tag + '\n')
        iframe_id = 'qwerty'
        browser.execute_script("$('iframe').attr('id', '%s');" % iframe_id)
        with browser.get_iframe(iframe_id) as iframe:
            iframe.find_by_tag('body').type(data['body'])

    def check_success_add_form(self, browser, data, check_success_message):
        # After login we see a profile link to our profile
        assert browser.is_text_present(check_success_message)
        assert browser.is_text_present(data['title'])
        assert browser.is_text_present(data['description'])
        for text in data['body'].split('\n'):
            assert browser.is_text_present(text.strip())

        for tag in data.get('tags', []):
            assert browser.is_text_present(tag)
        # TODO: add check that all submitted fields were checked here
