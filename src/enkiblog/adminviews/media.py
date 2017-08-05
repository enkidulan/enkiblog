import colander
import deform
from uuid import uuid4

from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing
from websauna.system.admin import views as adminviews
from deform.schema import FileData

from enkiblog.admins import MediaAdmin
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator
from enkiblog.core.deform.tempstorage import FileUploadTempStore


@colander.deferred
def deferred_file_upload_widget(node, kw):
    tmpstore = FileUploadTempStore(request=kw['request'])
    return deform.widget.FileUploadWidget(tmpstore)


fields = (
    colander.SchemaNode(
        colander.String(),
        name='description',
        required=False),
    colander.SchemaNode(
        FileData(),
        name='blob',
        required=False,
        widget=deferred_file_upload_widget)
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
        FileUploadTempStore(request=self.request).clear()

        return super().save_changes(form, appstruct, obj)


@view_overrides(context=MediaAdmin)
class MediaListing(adminviews.Listing):

    table = listing.Table(
        columns=[
            listing.Column("title", "Title"),
            listing.ControlsColumn(),
        ]
    )

    def order_query(self, query):
        """Sort the query."""
        return query.order_by('created_at')
