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

from enkiblog.core.deform.widgets import CKEditorWidget
from enkiblog.admins import PostAdmin
from enkiblog.models import Post, Tag
from enkiblog.core.utils import slugify


@colander.deferred
def deferred_tags_widget(_, kw):
    dbsession = kw['request'].dbsession
    vocab = [
        (uuid_to_slug(uuid), title)
        for uuid, title in dbsession.query(Tag.uuid, Tag.title).all()]
    return deform.widget.Select2Widget(
        values=vocab, multiple=True, css_class='tags-select2w')


@colander.deferred
def deferred_ckeditor_widget(*_):
    options = {}
    return CKEditorWidget(options=options)


@colander.deferred
def deferred_state_choices_widget(_, kw):
    request = kw['request']
    workflow = request.workflow
    workflow.state_info(None, request)
    context = None  # XXX: should be a resource model
    choices = [(w['name'], w['title']) for w in workflow.state_info(context, kw['request'])]
    return deform.widget.SelectWidget(values=choices)


@colander.deferred
def deferred_state_default(_, kw):
    workflow = kw['request'].workflow
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
        widget=deferred_ckeditor_widget),
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
    form_generator = SQLAlchemyFormGenerator(includes=POST_VIEWABLE_FIELDS)
    # TODO: on publishing publish all related content


@view_overrides(context=PostAdmin.Resource)
class PostShow(adminviews.Show):
    form_generator = SQLAlchemyFormGenerator(includes=POST_VIEWABLE_FIELDS)


def get_human_readable_date(field_name, _view, _column, obj):
    time = getattr(obj, field_name)
    return format_date(time) if time else ''


def post_navigate_url_getter(request, resource):
    return request.route_url('post', slug=resource.obj.slug)


@view_overrides(context=PostAdmin)
class PostsListing(adminviews.Listing):

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

    def order_query(self, query):
        """Sort the query."""
        return query.order_by('created_at')
