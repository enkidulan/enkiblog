import transaction
from uuid import uuid4


def test_create_post(site, navigator, admin_user, fakefactory):

    post = fakefactory.PostFactory.build()

    navigator = navigator(user=admin_user)
    navigator.submit(
        site.admin_menu.posts.add_post_page.add_post_form,
        data={
            "title": post.title,
            "descriptions": post.description,
            "body": post.body},
        status='success',
    )


def test_post_create_validation(site, navigator, admin_user, fakefactory):

    post = fakefactory.PostFactory.build()

    navigator = navigator(user=admin_user)
    navigator.submit(
        site.admin_menu.posts.add_post_page.add_post_form,
        data={
            "title": '',
            "descriptions": post.description,
            "body": post.body},
        status='validation_error',
    )


def test_delete_post(browser, navigator, admin_user, site, dbsession, fakefactory):

    with transaction.manager:
        fakefactory.PostFactory()
    navigator = navigator(user=admin_user)

    navigator.navigate(site.admin_menu.posts)

    assert browser.is_text_present("Total 1 item")

    browser.find_by_css('.btn-crud-listing-delete').click()
    assert browser.is_text_present("Confirm delete")

    browser.find_by_css('#btn-delete-yes').click()
    assert browser.is_text_present("Deleted")

    navigator.navigate(site.admin_menu.posts)
    assert browser.is_text_present("No items")


def test_list_posts(browser, site, navigator, admin_user, fakefactory, dbsession):

    with transaction.manager:
        fakefactory.PostFactory.create_batch(size=30)

    navigator = navigator(user=admin_user)
    navigator.navigate(site.admin_menu.posts)
    assert browser.is_text_present("Total 30 items")


def test_edit_post(browser, site, navigator, admin_user, fakefactory, dbsession):
    with transaction.manager:
        fakefactory.PostFactory()
        dbsession.expunge_all()

    navigator = navigator(user=admin_user)
    navigator.navigate(site.admin_menu.posts)

    navigator.browser.find_by_css('.btn-crud-listing-edit').click()
    assert browser.is_text_present("Editing")

    text = uuid4().hex
    browser.fill("title", text)
    browser.find_by_name("save").click()

    assert browser.is_text_present("Changes saved.")
    assert browser.is_text_present(text)
