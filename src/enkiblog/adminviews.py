"""Admin interface views and buttons."""

import colander
import deform
import string

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from websauna.system.core import messages
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing
from websauna.system.admin.views import Listing as DefaultListing
from websauna.system.admin.views import Add as DefaultAdd
from websauna.system.admin.views import Show as DefaultShow
from websauna.system.admin.views import Edit as DefaultEdit
from websauna.system.crud.views import ResourceButton
from websauna.system.crud.views import TraverseLinkButton
from websauna.system.form.csrf import CSRFSchema
from websauna.system.form.resourceregistry import ResourceRegistry
from websauna.system.form.schema import objectify, dictify
from websauna.system.http import Request
from websauna.utils.time import now

from .admins import PostAdmin
from .models import Post
from .utils import slugify


class PostSchema(CSRFSchema):

    title = colander.SchemaNode(colander.String(), required=True)

    descriptions = colander.SchemaNode(
        colander.String(),
        required=True,
        widget=deform.widget.TextAreaWidget(),)

    body = colander.SchemaNode(
        colander.String(),
        required=True,
        widget=deform.widget.TextAreaWidget(rows=40, css_class="body-text"))

    def dictify(self, obj) -> dict:
        appstruct = dictify(self, obj)
        return appstruct

    def objectify(self, appstruct: dict, obj):
        objectify(self, appstruct, obj)


@view_overrides(context=PostAdmin)
class PostAdd(DefaultAdd):

    def get_form(self):
        schema = PostSchema().bind(request=self.request)
        form = deform.Form(schema, buttons=self.get_buttons(), resource_registry=ResourceRegistry(self.request))
        return form

    def add_object(self, obj):

        dbsession = self.context.get_dbsession()

        obj.slug = slugify(obj.title, Post.slug, dbsession)
        obj.author = self.request.user.username

        # Make sure we autogenerate a slug
        dbsession.add(obj)
        dbsession.flush()
