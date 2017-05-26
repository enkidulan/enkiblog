from websauna.system.admin.modeladmin import model_admin
from websauna.system.admin.modeladmin import ModelAdmin

# Import our models
from . import models
from websauna.system.crud import listing


@model_admin(traverse_id="posts")
class PostAdmin(ModelAdmin):
    title = "Posts"

    singular_name = "post"
    plural_name = "posts"

    model = models.Post

    class Resource(ModelAdmin.Resource):

        def get_title(self):
            return self.get_object().title


@model_admin(traverse_id="media")
class MediaAdmin(ModelAdmin):
    title = "Media"

    singular_name = "media"
    plural_name = "media"

    model = models.Media

    class Resource(ModelAdmin.Resource):

        def get_title(self):
            return self.get_object().title


@model_admin(traverse_id="tags")
class TagAdmin(ModelAdmin):
    title = "Tags"

    singular_name = "tag"
    plural_name = "tags"

    model = models.Tag

    class Resource(ModelAdmin.Resource):

        def get_title(self):
            return self.get_object().title
