from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from websauna.system.core.views.notfound import notfound

from enkiblog import models


@view_config(context=NoResultFound)
def failed_validation(exc, request):
    return notfound(request)


class VistorsResources:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession
        # self.posts_query = self.dbsession.query(models.Post).filter_by(state='published')
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

        # import pdb; pdb.set_trace()

        post_subquery = self.posts_query.subquery('post_subquery')

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
        query_post = dbsession.query(models.Post).filter(models.Post.slug == neighbors.c.current)
        posts = query_post.join(neighbors, neighbors.c.current == models.Post.slug)
        post, slug_prev, slug_next = posts.add_columns(neighbors.c.prev, neighbors.c.next).one()

        return {
            "project": "enkiblog",
            'post': post,
            'prev_link': slug_prev and self.request.route_url("post", slug=slug_prev),
            'next_link': slug_next and self.request.route_url("post", slug=slug_next),
        }


@view_config(route_name='media')
def favicon_view(context, request):
    query = request.dbsession.query(models.Media).filter_by(
        state='published', slug=request.matchdict["slug"])
    obj = query.one()
    return Response(content_type=obj.mimetype, body=obj.blob)
