import colander
import deform
from uuid import uuid4

from websauna.system.core.viewconfig import view_overrides
from websauna.system.admin import views as adminviews
from deform.schema import FileData

from enkiblog.admins import MediaAdmin
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator


class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""

    def preview_url(self, uid):
        return None


# TODO: make one as in https://github.com/Pylons/substanced/blob/7761ae17759139019449a1872a46ff53bfd528bb/substanced/form/__init__.py#L111
tmpstore = MemoryTmpStore()  # XXX:


fields = (
    colander.SchemaNode(
        colander.String(),
        name='description',
        required=False),
    colander.SchemaNode(
        FileData(),
        name='blob',
        required=False,
        widget=deform.widget.FileUploadWidget(tmpstore))
)


def marshal_appstruct_for_file_data(appstruct, field='blob'):
    appstruct['title'] = appstruct[field]['filename']
    appstruct['slug'] = uuid4().hex + '-' + appstruct[field]['filename']
    appstruct['mimetype'] = appstruct[field]['mimetype']
    appstruct[field] = appstruct[field]['fp'].read()


@view_overrides(context=MediaAdmin)
class MediaAdd(adminviews.Add):

    form_generator = SQLAlchemyFormGenerator(includes=fields)

    def build_object(self, form, appstruct):

        marshal_appstruct_for_file_data(appstruct)
        appstruct['author'] = self.request.user

        return super().build_object(form, appstruct)


@view_overrides(context=MediaAdmin.Resource)
class MediaEdit(adminviews.Edit):
    form_generator = SQLAlchemyFormGenerator(includes=list(fields) + ['state'])

    def get_appstruct(self, form, obj):
        """Turn the object to form editable format."""
        appstruct = form.schema.dictify(obj)
        appstruct['blob'] = {
            'fp': None,
            'filename': obj.title,
            'mimetype': obj.mimetype,
            'uid': uuid4().hex,
        }
        return appstruct

    def save_changes(self, form: deform.Form, appstruct: dict, obj: object):
        # TODO: do not ovveride slug

        marshal_appstruct_for_file_data(appstruct)
        appstruct['author'] = self.request.user

        return super().save_changes(form, appstruct, obj)
