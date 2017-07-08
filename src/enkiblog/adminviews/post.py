""" Admin views for post content type"""
from functools import partial
import colander
import deform
from babel.dates import format_date

from websauna.system.admin import views as adminviews
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator
from websauna.system.form.sqlalchemy import UUIDModelSet
from websauna.system.crud import listing
from websauna.utils.slug import uuid_to_slug

from enkiblog.deform_widgets import CKEditorWidget
from enkiblog.admins import PostAdmin
from enkiblog.models import Post, Tag
from enkiblog.utils import slugify


@colander.deferred
def deferred_tags_widget(node, kwags):  # pylint: disable=unused-argument
    """ Tags select widget """
    # TODO: make it search based
    dbsession = kwags['request'].dbsession
    vocab = [
        (uuid_to_slug(uuid), title)
        for uuid, title in dbsession.query(Tag.uuid, Tag.title).all()]
    return deform.widget.Select2Widget(
        values=vocab, multiple=True, css_class='tags-select2w')


@colander.deferred
def deferred_state_choices_widget(node, kwags):  # pylint: disable=unused-argument
    """ State select widget """
    request = kwags['request']
    workflow = request.workflow
    workflow.state_info(None, request)
    context = None  # TODO: should be a resource model
    choices = [(w['name'], w['title']) for w in workflow.state_info(context, kwags['request'])]
    return deform.widget.SelectWidget(values=choices)


@colander.deferred
def deferred_state_default(node, kwags):  # pylint: disable=unused-argument
    """ State default value widget """
    workflow = kwags['request'].workflow
    return workflow.initial_state


POST_EDITABLE_FIELDS = [
    "title",
    colander.SchemaNode(
        colander.String(),
        name="description",
        required=True),
    colander.SchemaNode(
        UUIDModelSet(model=Tag, match_column="uuid"),
        name='tags',
        widget=deferred_tags_widget,
        missing=None),
    colander.SchemaNode(
        colander.String(),
        name="body",
        required=True,
        widget=CKEditorWidget()),
    colander.SchemaNode(
        colander.String(),
        name="state",
        required=True,
        default=deferred_state_default,
        widget=deferred_state_choices_widget),
]

POST_VIEWABLE_FIELDS = POST_EDITABLE_FIELDS + [
    "uuid",
    "created_at",
    "published_at",
    "updated_at",
    "slug",
    "author",
]


@view_overrides(context=PostAdmin)
class PostAdd(adminviews.Add):
    """ Add form """

    form_generator = SQLAlchemyFormGenerator(includes=POST_EDITABLE_FIELDS)

    def add_object(self, obj):
        dbsession = self.context.get_dbsession()
        obj.author = self.request.user
        with dbsession.no_autoflush:
            obj.slug = slugify(obj.title, Post.slug, dbsession)
        dbsession.add(obj)
        dbsession.flush()


@view_overrides(context=PostAdmin.Resource)
class PostEdit(adminviews.Edit):
    """ Edit form """

    form_generator = SQLAlchemyFormGenerator(includes=POST_VIEWABLE_FIELDS)
    # TODO: on publishing publish all related content
    # TODO: use worflow for publising posts


@view_overrides(context=PostAdmin.Resource)
class PostShow(adminviews.Show):
    """ View form """

    form_generator = SQLAlchemyFormGenerator(includes=POST_VIEWABLE_FIELDS)


def get_human_readable_date(field_name, view, column, obj):  # pylint: disable=unused-argument
    """ listing item view helper """
    time = getattr(obj, field_name)
    return format_date(time) if time else ''


def post_navigate_url_getter(request, resource):
    """ listing item view helper """
    return request.route_url('post', slug=resource.obj.slug)


@view_overrides(context=PostAdmin)
class PostsListing(adminviews.Listing):
    """ Listing view """

    table = listing.Table(
        columns=[
            listing.Column("title", "Title", navigate_url_getter=post_navigate_url_getter),
            listing.Column("state", "State"),
            listing.Column(
                "created_at",
                "Created",
                getter=partial(get_human_readable_date, 'created_at')),
            listing.Column(
                "published_at",
                "Published",
                getter=partial(get_human_readable_date, 'published_at')),
            listing.ControlsColumn(),
        ]
    )
