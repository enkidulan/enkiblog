import transaction
from .common import check_if_widget_itmes_present

def test_on_recent_posts_widget_user_sees_ordered_published_items(
        browser, web_server, site, navigator, fakefactory, dbsession):

    shown_items_number = 10

    with transaction.manager:
        posts = fakefactory.PostFactory.create_batch(shown_items_number + 5)[::-1]
        dbsession.expunge_all()
    navigator().navigate(site)

    check_if_widget_itmes_present('.recent', browser, posts[:shown_items_number], web_server)


def test_on_recent_posts_widget_user_doesnt_see_not_published_posts(
        web_server, browser, site, navigator, fakefactory, dbsession):

    with transaction.manager:
        post = fakefactory.PostFactory()
        fakefactory.PostFactory.create_batch(2, state='draft')
        dbsession.expunge_all()
    navigator().navigate(site, check_if_navigated=False)

    assert len(browser.find_by_css('.recent .list-group-item')) == 1
    assert browser.find_by_css('.recent .list-group-item-heading').text == post.title
