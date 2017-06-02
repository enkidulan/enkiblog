import transaction


def test_on_home_page_user_is_redirected_to_newest_post(
        browser, site, navigator, fakefactory, dbsession):

    with transaction.manager:
        fakefactory.PostFactory.create_batch(2)
        post = fakefactory.PostFactory()
        dbsession.expunge_all()

    navigator().navigate(site, check_if_navigated=False)

    assert browser.is_text_present(post.title)
    assert browser.url.endswith('/programming/' + post.slug)
