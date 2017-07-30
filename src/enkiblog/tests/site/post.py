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
        browser.execute_script("$('iframe').contents().find('body').text('%s')" % data['body'])
        browser.fill("description", data['description'])
        # adding tags
        tags_input = browser.find_by_xpath('//select[@name="tags"]/following::input[@type="search"]')[0]
        for tag in data.get('tags', []):
            tags_input.type(tag + '\n')

    def check_success_add_form(self, browser, data, check_success_message):
        # After login we see a profile link to our profile
        assert browser.is_text_present(check_success_message)
        assert browser.is_text_present(data['title'])
        assert browser.is_text_present(data['description'])
        assert browser.is_text_present(data['body'])

        for tag in data.get('tags', []):
            assert browser.is_text_present(tag)
        # TODO: add check that all submitted fields were checked here
