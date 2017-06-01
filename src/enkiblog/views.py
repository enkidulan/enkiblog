from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from websauna.system.core.views.notfound import notfound

from enkiblog import models


@view_config(context=NoResultFound)
def failed_validation(exc, request):
    return notfound(request)


def get_recent_posts(dbsession, posts_query, num=10):
    return posts_query.options(joinedload('tags')).order_by(models.Post.published_at.desc()).limit(num).all()


def get_similar_posts(dbsession, post, posts_query, num=10):
    # simply finds other posts with common most tags
    f_tag_uuid = models.AssociationPostsTags.tag_uuid
    f_post_uuid = models.AssociationPostsTags.post_uuid

    post_tags = dbsession.query(f_tag_uuid).filter(
        f_post_uuid == post.uuid)

    return dbsession.query(models.Post)\
        .filter(f_post_uuid.in_(posts_query.with_entities(models.Post.uuid)))\
        .filter(f_tag_uuid.in_(post_tags))\
        .filter(f_post_uuid == models.Post.uuid)\
        .filter(f_post_uuid != post.uuid)\
        .group_by(f_post_uuid, models.Post.uuid)\
        .order_by(desc(func.count(f_post_uuid)))\
        .options(joinedload('tags'))\
        .limit(num)\
        .all()


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
            'recent': get_recent_posts(dbsession, self.posts_query),
            'similar': get_similar_posts(dbsession, post, self.posts_query),
        }


@view_config(route_name='media')
def media_view(context, request):
    query = request.dbsession.query(models.Media).filter_by(
        state='published', slug=request.matchdict["slug"])
    obj = query.one()
    return Response(content_type=obj.mimetype, body=obj.blob)
