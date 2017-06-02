
def check_if_widget_itmes_present(base_selector, browser, items, web_server):
    recent_items = browser.find_by_css(base_selector + ' .list-group-item')
    assert len(recent_items) == len(items)
    for item, post in zip(recent_items, items):
        assert item.find_by_css('.list-group-item-heading').text == post.title
        for tag in post.tags:
            assert tag.title in item.find_by_css('.list-group-item-text').text

    # dummy link redirect test
    item.click()  # add some sleep?
    assert browser.url == web_server + '/programming/' + post.slug
