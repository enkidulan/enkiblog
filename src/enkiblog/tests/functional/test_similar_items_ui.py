# pylint: disable=invalid-name, too-many-arguments
import transaction
import random
from .common import check_if_widget_itmes_present


def test_on_similar_posts_widget_user_sees_ordered_published_items(
        browser, web_server, site, navigator, fakefactory, dbsession):

    shown_items_number = 10
    shared_tags_number = shown_items_number * 3
    total_tags_number = shared_tags_number * 3

    with transaction.manager:

        tags = fakefactory.TagFactory.create_batch(size=total_tags_number)
        random.shuffle(tags)

        tags, noise_tags = tags[:shared_tags_number], tags[shared_tags_number:]
        post = fakefactory.PostFactory(tags=tags)

        tags_sets = [tags[i:] for i, _ in enumerate(tags)]
        random.shuffle(tags_sets)

        similar_posts = []
        for tag_sets in tags_sets:
            fakefactory.PostFactory(tags=random.sample(noise_tags, shown_items_number))
            post_tags = tag_sets + fakefactory.TagFactory.create_batch(size=shown_items_number)
            similar_posts.append(fakefactory.PostFactory(tags=random.sample(post_tags, len(post_tags))))
            fakefactory.PostFactory(tags=random.sample(noise_tags, shown_items_number))
        similar_posts.sort(key=lambda i: len(i.tags), reverse=True)
        dbsession.expunge_all()

    navigator().navigate(site)
    # XXX: redesign url making func, currently is inflexible
    browser.visit(web_server + '/programming/' + post.slug)
    check_if_widget_itmes_present(
        '.similar', browser, similar_posts[:shown_items_number], web_server)


def test_on_similar_posts_widget_user_doesnt_see_not_published_posts(
        web_server, browser, site, navigator, fakefactory, dbsession):

    with transaction.manager:
        tags = fakefactory.TagFactory.create_batch(size=2)
        post = fakefactory.PostFactory(tags=tags)
        similar_post = fakefactory.PostFactory(tags=tags)
        fakefactory.PostFactory.create_batch(2, state='draft', tags=tags)
        dbsession.expunge_all()

    navigator().navigate(site)
    # XXX: redesign url making func, currently is inflexible
    browser.visit(web_server + '/programming/' + post.slug)

    assert len(browser.find_by_css('.similar .list-group-item')) == 1
    assert browser.find_by_css('.similar .list-group-item-heading').text == similar_post.title
