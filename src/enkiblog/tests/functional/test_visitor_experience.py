import transaction


def test_on_home_page_user_is_redirected_to_newest_post(
        browser, site, navigator, fakefactory, dbsession):

    with transaction.manager:
        fakefactory.PostFactory.create_batch(2)
        post = fakefactory.PostFactory()
        dbsession.expunge_all()

    navigator().navigate(site, check_if_navigated=False)

    assert browser.is_text_present(post.title)
    assert browser.url.endswith('/posts/' + post.slug)


def test_user_doesnt_see_not_published_posts(
        web_server, browser, site, navigator, fakefactory, dbsession):

    with transaction.manager:
        post = fakefactory.PostFactory(state='draft')
        dbsession.expunge_all()

    navigator().navigate(site, check_if_navigated=False)

    # doesn`t redirect to unpublished posts
    assert browser.is_text_present('There is nothing here yet...')
    assert not browser.url.endswith('/posts/' + post.slug)

    # post is not accessible by url
    browser.visit(web_server + '/posts/' + post.slug)
    assert browser.is_text_present('Not found')


def test_user_can_navigate_by_paginator_between_posts(
        web_server, browser, site, navigator, fakefactory, dbsession):

    with transaction.manager:
        posts = fakefactory.PostFactory.create_batch(3)
        for post in posts:  # creating noise
            fakefactory.PostFactory(published_at=post.published_at, state='draft')
        dbsession.expunge_all()

    navigator().navigate(site)

    assert browser.find_by_css('#post-prev').has_class('disabled')
    assert not browser.find_by_css('#post-next').has_class('disabled')

    for post in posts[::-1]:
        post_page = navigator().parse(site.post)
        assert post_page.title == post.title
        assert post_page.slug == post.slug
        browser.find_by_css('#post-next').click()

    assert not browser.find_by_css('#post-prev').has_class('disabled')
    assert browser.find_by_css('#post-next').has_class('disabled')

    for post in posts:
        post_page = navigator().parse(site.post)
        assert post_page.title == post.title
        assert post_page.slug == post.slug
        browser.find_by_css('#post-prev').click()

    assert browser.find_by_css('#post-prev').has_class('disabled')
    assert not browser.find_by_css('#post-next').has_class('disabled')
