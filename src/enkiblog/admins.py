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
