""" Admins views and resources declarations """
from websauna.system.admin.modeladmin import model_admin
from websauna.system.admin.modeladmin import ModelAdmin

from . import models


@model_admin(traverse_id="posts")
class PostAdmin(ModelAdmin):
    """ Post admin view """
    title = "Posts"
    singular_name = "post"
    plural_name = "posts"
    model = models.Post

    class Resource(ModelAdmin.Resource):
        """ Post admin resource """

        def get_title(self):
            return self.get_object().title


@model_admin(traverse_id="media")
class MediaAdmin(ModelAdmin):
    """ Media admin view """
    title = "Media"
    singular_name = "media"
    plural_name = "media"
    model = models.Media

    class Resource(ModelAdmin.Resource):
        """ Media admin resource """

        def get_title(self):
            return self.get_object().title


@model_admin(traverse_id="tags")
class TagAdmin(ModelAdmin):
    """ Tag admin view """
    title = "Tags"
    singular_name = "tag"
    plural_name = "tags"
    model = models.Tag

    class Resource(ModelAdmin.Resource):
        """ Tag admin resource """

        def get_title(self):
            return self.get_object().title
