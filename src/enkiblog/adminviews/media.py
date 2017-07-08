""" Admin views for media content type"""
from uuid import uuid4

import colander
import deform
from deform.schema import FileData
from websauna.system.core.viewconfig import view_overrides
from websauna.system.admin import views as adminviews
from websauna.system.crud import listing
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator

from enkiblog.admins import MediaAdmin
from enkiblog.core.forms import FileUploadTempStore


@colander.deferred
def file_upload_widget(node, kwags):  # pylint: disable=unused-argument
    """
    File upload widget based on file tmp session storage, requires storage clean
    up on success or cancellation
    """
    request = kwags['request']
    tmpstore = FileUploadTempStore(request)
    widget = deform.widget.FileUploadWidget(tmpstore)
    return widget


MEDIA_FORM_FIELDS = (
    colander.SchemaNode(
        colander.String(),
        name='description',
        required=False),
    colander.SchemaNode(
        FileData(),
        name='blob',
        required=False,
        widget=file_upload_widget)
)


def marshal_appstruct_for_file_data(appstruct, field='blob'):
    """ Mainly this is a marshaler for file upload widget field """
    appstruct['title'] = appstruct[field]['filename']
    if 'slug' not in appstruct:
        appstruct['slug'] = uuid4().hex + '-' + appstruct[field]['filename']
    appstruct['mimetype'] = appstruct[field]['mimetype']
    appstruct[field] = appstruct[field]['fp'].read()


@view_overrides(context=MediaAdmin)
class MediaAdd(adminviews.Add):
    """ Add form of media object """

    form_generator = SQLAlchemyFormGenerator(includes=MEDIA_FORM_FIELDS)

    def build_object(self, form, appstruct):
        """ Marshales file upload data and creates recordable object """
        marshal_appstruct_for_file_data(appstruct)
        appstruct['author'] = self.request.user
        return super().build_object(form, appstruct)

    def do_success(self, resource):
        """ Cleans upload widget file temp store  """
        FileUploadTempStore(self.request).clear()
        return super().do_success(resource)


@view_overrides(context=MediaAdmin.Resource)
class MediaEdit(adminviews.Edit):
    """ Edit form of media object """

    form_generator = SQLAlchemyFormGenerator(includes=MEDIA_FORM_FIELDS + ('state', ))

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
        """ Marshales file upload data and save changes """
        marshal_appstruct_for_file_data(appstruct)
        appstruct['author'] = self.request.user
        return super().save_changes(form, appstruct, obj)

    def do_success(self):
        """ Cleans upload widget file temp store  """
        FileUploadTempStore(self.request).clear()
        return super().do_success()


def navigate_url_getter(request, resource):
    """ Extract navigable link for media object """
    return request.route_url('media', slug=resource.obj.slug)


@view_overrides(context=MediaAdmin)
class MediaListing(adminviews.Listing):
    """ Listing view of media object """

    table = listing.Table(
        columns=[
            listing.Column("title", "Title", navigate_url_getter=navigate_url_getter),
            listing.Column("state", "State"),
            listing.Column("author", "Author"),
            listing.ControlsColumn(),
        ]
    )
