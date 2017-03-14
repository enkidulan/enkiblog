from pyramid.httpexceptions import HTTPFound
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
        self.posts_query = self.dbsession.query(
            models.Post).filter_by(state='published').order_by(models.Post.published_at.desc())

    @view_config(route_name="home", renderer='enkiblog/home.html')
    def home(self):
        post = self.posts_query.first()
        if post is not None:
            return HTTPFound(self.request.route_url("posts", slug=post.slug))
        return {"project": "enkiblog"}

    @view_config(route_name="posts", renderer='enkiblog/posts.html')
    def posts(self):
        dbsession = self.dbsession
        slug = self.request.matchdict["slug"]

        post_subquery = self.posts_query.subquery('post_subquery')
        neighborhood = dbsession.query(
            post_subquery.c.slug.label('current'),
            func.lag(post_subquery.c.slug).over().label('prev'),
            func.lead(post_subquery.c.slug).over().label('next')
        ).subquery('neighborhood')
        neighbors = dbsession.query(neighborhood).filter(
            neighborhood.c.current == slug).subquery('neighbors')
        query_post = dbsession.query(models.Post).filter(models.Post.slug == neighbors.c.current)
        posts = query_post.join(neighbors, neighbors.c.current == models.Post.slug)
        post, slug_prev, slug_next = posts.add_columns(neighbors.c.prev, neighbors.c.next).one()

        return {
            "project": "enkiblog",
            'post': post,
            'prev_link': slug_prev and self.request.route_url("posts", slug=slug_prev),
            'next_link': slug_next and self.request.route_url("posts", slug=slug_next),
        }
