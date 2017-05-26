"""Admin interface views and buttons."""

import colander
import deform

from websauna.system.core.viewconfig import view_overrides
from websauna.system.admin.views import Add as DefaultAdd
from websauna.system.form.csrf import CSRFSchema
from websauna.system.form.resourceregistry import ResourceRegistry
from websauna.system.form.schema import objectify, dictify
from deform.schema import FileData
from websauna.system.form.sqlalchemy import UUIDForeignKeyValue, UUIDModelSet

from sqlalchemy.orm.collections import InstrumentedList

from .admins import PostAdmin, MediaAdmin
from .models import Post, Media, Tag, AssociationPostsTags
from .utils import slugify
from websauna.utils.slug import uuid_to_slug


@colander.deferred
def deferred_tags_widget(node, kw):
    dbsession = kw['request'].dbsession
    vocab = [
        (uuid_to_slug(uuid), title)
        for uuid, title in dbsession.query(Tag.uuid, Tag.title).all()]
    return deform.widget.Select2Widget(
        values=vocab, multiple=True, css_class='tags-select2w')


class PostSchema(CSRFSchema):

    title = colander.SchemaNode(colander.String(), required=True)

    descriptions = colander.SchemaNode(
        colander.String(),
        required=True,
        widget=deform.widget.TextAreaWidget(),)

    tags = colander.SchemaNode(
        UUIDModelSet(model=Tag, match_column="uuid"),
        widget=deferred_tags_widget,
        missing=None)

    body = colander.SchemaNode(
        colander.String(),
        required=True,
        widget=deform.widget.TextAreaWidget(rows=40, css_class="body-text"))

    def dictify(self, obj) -> dict:
        appstruct = dictify(self, obj)
        return appstruct

    def objectify(self, appstruct: dict, obj):
        objectify(self, appstruct, obj)

# from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator


@view_overrides(context=PostAdmin)
class PostAdd(DefaultAdd):

    # TODO: try form_generator = SQLAlchemyFormGenerator(includes=includes)

    def get_form(self):
        schema = PostSchema().bind(request=self.request)
        form = deform.Form(
            schema, buttons=self.get_buttons(), resource_registry=ResourceRegistry(self.request))
        return form

    def add_object(self, obj):

        dbsession = self.context.get_dbsession()

        obj.author = self.request.user

        with dbsession.no_autoflush:
            obj.slug = slugify(obj.title, Post.slug, dbsession)

        dbsession.add(obj)
        dbsession.flush()


class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""

    def preview_url(self, uid):
        return None


tmpstore = MemoryTmpStore()


class MediaSchema(CSRFSchema):

    descriptions = colander.SchemaNode(
        colander.String(),
        required=True,
        widget=deform.widget.TextAreaWidget(),)

    blob = colander.SchemaNode(
        FileData(),
        required=True,
        widget=deform.widget.FileUploadWidget(tmpstore))

    def dictify(self, obj) -> dict:
        appstruct = dictify(self, obj)
        return appstruct

    def objectify(self, appstruct: dict, obj):
        objectify(self, appstruct, obj)


@view_overrides(context=MediaAdmin)
class MediaAdd(DefaultAdd):

    def get_form(self):
        schema = MediaSchema().bind(request=self.request)
        form = deform.Form(
            schema, buttons=self.get_buttons(), resource_registry=ResourceRegistry(self.request))
        return form

    def add_object(self, obj):

        dbsession = self.context.get_dbsession()

        obj.title = obj.blob['filename']
        obj.slug = obj.blob['filename']
        obj.author = self.request.user
        obj.mimetype = obj.blob['mimetype']

        # XXX: so far so good
        obj.blob = obj.blob['fp'].read()

        dbsession.add(obj)
        dbsession.flush()
