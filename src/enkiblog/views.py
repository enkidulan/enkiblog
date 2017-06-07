from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from websauna.system.core.views.notfound import notfound

from enkiblog import models

from pyramid.events import subscriber
from websauna.system.core.events import InternalServerError
from websauna.system.core.loggingcapture import get_logging_user_context
from pyramid_layout.panel import panel_config


@panel_config('recent_items_widget', renderer='templates/enkiblog/listing_items_widget.pt')
def recent_items_widget(context, request, num=10, title='Recent posts'):
    posts_query = models.Post.acl_aware_listing_query(
        dbsession=request.dbsession,
        effective_principals=request.effective_principals,
        actions=('view',),
        user=request.user)
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

    posts_query = models.Post.acl_aware_listing_query(
        dbsession=dbsession,
        effective_principals=request.effective_principals,
        actions=('view',),
        user=request.user)

    post_tags = dbsession.query(f_tag_uuid).filter(
        f_post_uuid == post.uuid)

    items = dbsession.query(models.Post)\
        .filter(f_post_uuid.in_(posts_query.with_entities(models.Post.uuid)))\
        .filter(f_tag_uuid.in_(post_tags))\
        .filter(f_post_uuid == models.Post.uuid)\
        .filter(f_post_uuid != post.uuid)\
        .group_by(f_post_uuid, models.Post.uuid)\
        .order_by(desc(func.count(f_post_uuid)))\
        .options(joinedload('tags'))\
        .limit(num)\
        .all()

    return {'items': items, 'title': title}


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
        # TODO: make it sense to switch to only published posts? ^
        self.posts_query = models.Post.acl_aware_listing_query(
            dbsession=self.dbsession,
            effective_principals=request.effective_principals,
            actions=('view',),
            user=request.user)
        self.posts_query = self.posts_query.order_by(models.Post.published_at.desc())
        # TODO: add test to show only public posts

    @view_config(route_name="home", renderer='enkiblog/home.html')
    def home(self):
        post = self.posts_query.first()
        if post is not None:
            return HTTPFound(self.request.route_url("post", slug=post.slug))
        return {"project": "enkiblog"}

    @view_config(route_name="post", renderer='enkiblog/post.html')
    def post(self):
        dbsession = self.dbsession
        slug = self.request.matchdict["slug"]

        posts_query = self.posts_query.options(joinedload('tags'))
        post_subquery = posts_query.subquery('post_subquery')

        # TODO: investigate case - probably after union issue
        # XXX: actually important issue - need to be fixed
        slug_field = post_subquery.c.slug if hasattr(post_subquery.c, 'slug') else post_subquery.c.posts_slug

        neighborhood = dbsession.query(
            slug_field.label('current'),
            func.lag(slug_field).over().label('prev'),
            func.lead(slug_field).over().label('next')
        ).subquery('neighborhood')
        neighbors = dbsession.query(neighborhood).filter(
            neighborhood.c.current == slug).subquery('neighbors')
        query_post = posts_query.filter(models.Post.slug == neighbors.c.current)
        posts = query_post.join(neighbors, neighbors.c.current == models.Post.slug)

        # TODO: .one() doesn't work - investigate
        result = posts.add_columns(neighbors.c.prev, neighbors.c.next).first()
        if result is None:
            raise NoResultFound()
        post, slug_prev, slug_next = result

        return {
            'project': 'enkiblog',
            'post': post,
            'tags': post.tags,
            'prev_link': slug_prev and self.request.route_url("post", slug=slug_prev),
            'next_link': slug_next and self.request.route_url("post", slug=slug_next),
        }


@view_config(route_name='media')
def media_view(context, request):
    query = models.Media.acl_aware_listing_query(
        dbsession=request.dbsession,
        effective_principals=request.effective_principals,
        actions=('view',),
        user=request.user)
    obj = query.filter_by(slug=request.matchdict["slug"]).one()
    return Response(content_type=obj.mimetype, body=obj.blob)


@view_config(route_name="old_post")
def old_posts_redirect_view(context, request):
    return HTTPFound(request.route_url("post", slug=request.matchdict["slug"]))
