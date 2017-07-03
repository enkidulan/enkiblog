import os.path
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import func, desc, asc, select
from sqlalchemy.orm import joinedload, subqueryload, load_only, aliased
from sqlalchemy.orm.exc import NoResultFound
from websauna.system.core.views.notfound import notfound

from enkiblog import models

from pyramid.events import subscriber
from websauna.system.core.events import InternalServerError
from websauna.system.core.loggingcapture import get_logging_user_context
from pyramid_layout.panel import panel_config


EMPTY_TUPLE = tuple()


_icon = open(os.path.join(os.path.dirname(__file__), 'static', 'favicon.ico'), 'rb').read()
_fi_response = Response(content_type='image/x-icon', body=_icon)


@view_config(name='favicon.ico')
def favicon_view(context, request):
    return _fi_response


@panel_config('meta_tags', renderer='templates/enkiblog/meta_tags.pt')
def meta_tags(context, request):
    return {
        'tags': ','.join(map(str, getattr(context, 'tags', EMPTY_TUPLE))),
        'title': str(context),
        'description': context.description,
        'site_name': 'Enkidu\'s Blog',  # XXX: get from settings
    }


@panel_config('recent_items_widget', renderer='templates/enkiblog/listing_items_widget.pt')
def recent_items_widget(context, request, num=10, title='Recent posts'):
    posts_query = request.dbsession.query(models.Post).acl_filter(request)
    items = posts_query\
        .options(joinedload('tags'))\
        .order_by(models.Post.published_at.desc())\
        .limit(num)\
        .all()
    return {'items': items, 'title': title}


@panel_config('similar_items_widget', renderer='templates/enkiblog/listing_items_widget.pt')
def similar_items_widget(context, request, num=10, title='Similar posts'):
    # simply finds other posts with common most tags
    f_tag_uuid = models.AssociationPostsTags.tag_uuid
    f_post_uuid = models.AssociationPostsTags.post_uuid
    dbsession = request.dbsession
    post = context

    post_tags = dbsession.query(f_tag_uuid).filter(
        f_post_uuid == post.uuid)
    post_uuid = models.Post.uuid.label("post_uuid")
    relevance = func.count(f_post_uuid).label("relevance")

    allowed_to_see_sbr = dbsession.query(models.Post.uuid)\
        .acl_filter(request)\
        .subquery('allowed_to_see_sbr')

    related_posts_sbr = dbsession.query(f_post_uuid)\
        .filter(f_tag_uuid.in_(post_tags))\
        .filter(f_post_uuid == post_uuid)\
        .filter(f_post_uuid.in_(allowed_to_see_sbr))\
        .group_by(f_post_uuid)\
        .order_by(relevance)\
        .limit(num + 1)\
        .subquery('related_posts_sbr')

    items = dbsession.query(models.Post)\
        .options(joinedload('tags'))\
        .filter(models.Post.uuid.in_(related_posts_sbr))\
        .limit(num + 1)\
        .all()
    # TODO: order for showed items is not preserved

    # NOTE: checking not-equal outside SQL really gives performance increase
    items = tuple(i for i in items if i.uuid != post.uuid)
    return {'items': items[:num], 'title': title}


# https://github.com/websauna/websauna.sentry/blob/master/websauna/sentry/subscribers.py#L14
@subscriber(InternalServerError)
def notify_raven(event):
    request = event.request
    user_context = get_logging_user_context(request)
    request.raven.user_context(user_context)
    request.raven.captureException()


@view_config(context=NoResultFound)
def failed_validation(exc, request):
    return notfound(request)

# TODO: not found return and not raise found leads to different pages - fix that


class VistorsResources:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession
        # self.posts_query = self.dbsession.query(models.Post).filter_by(state='published')
        # TODO: make it sense to switch to only published posts? ^ make a mark for posts that are not public
        self.posts_query = self.dbsession.query(models.Post).acl_filter(request)
        # self.posts_query = self.posts_query.order_by(models.Post.published_at.desc())
        # TODO: add test to show only public posts

    @view_config(route_name="home", renderer='enkiblog/home.html')
    def home(self):
        post = self.posts_query.order_by(models.Post.published_at.desc()).first()
        if post is not None:
            return HTTPFound(self.request.route_url("post", slug=post.slug))
        return {"project": "enkiblog"}

    @view_config(route_name="post", renderer='enkiblog/post.html', permission='view')
    def post(self):
        slug = self.request.matchdict["slug"]

        posts_query = self.posts_query.options(joinedload('tags'))

        item = posts_query.filter(models.Post.slug == slug).one()
        prev_item = posts_query.filter(models.Post.published_at > item.published_at).order_by(models.Post.published_at).first()
        next_item = posts_query.filter(models.Post.published_at < item.published_at).order_by(models.Post.published_at.desc()).first()

        post, slug_prev, slug_next = item, getattr(prev_item, 'slug', None), getattr(next_item, 'slug', None)

        return {
            'project': 'enkiblog',
            'post': post,
            'tags': post.tags,
            'prev_link': slug_prev and self.request.route_url("post", slug=slug_prev),
            'next_link': slug_next and self.request.route_url("post", slug=slug_next),
        }


@view_config(route_name='media')
def media_view(context, request):
    query = request.dbsession.query(models.Media).acl_filter(request)
    obj = query.filter_by(slug=request.matchdict["slug"]).one()
    return Response(content_type=obj.mimetype, body=obj.blob)


@view_config(route_name="old_post")
def old_posts_redirect_view(context, request):
    return HTTPFound(request.route_url("post", slug=request.matchdict["slug"]))
