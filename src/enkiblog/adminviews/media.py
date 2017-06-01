import colander
import deform

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


tmpstore = MemoryTmpStore()  # XXX


@view_overrides(context=MediaAdmin)
class MediaAdd(adminviews.Add):
    fields = (
        colander.SchemaNode(
            colander.String(),
            name='description',
            required=False),
        colander.SchemaNode(
            FileData(),
            name='blob',
            required=True,
            widget=deform.widget.FileUploadWidget(tmpstore))
    )

    form_generator = SQLAlchemyFormGenerator(includes=fields)

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
