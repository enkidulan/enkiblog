import os
import os.path
import shutil
from uuid import uuid4


_marker = object()


class FileUploadTempStore(object):
    """ A Deform ``FileUploadTempStore`` implementation that stores file
    upload data in the Pyramid session and on disk.  The request passed to
    its constructor must be a fully-initialized Pyramid request (it have a
    ``registry`` attribute, which must have a ``settings`` attribute, which
    must be a dictionary).  The ``substanced.uploads_tempdir`` variable in the
    ``settings`` dictionary must be set to the path of an existing directory
    on disk.  This directory will temporarily store file upload data on
    behalf of Deform and Substance D when a form containing a file upload
    widget fails validation.
    See the :term:`Deform` documentation for more information about
    ``FileUploadTempStore`` objects.
    """

    tmpdir_path = 'websauna.uploads_tempdir'
    session_storage_name = 'websauna.tempstore'

    def __init__(self, request):
        self.tempdir = request.registry.settings[self.tmpdir_path]
        os.makedirs(self.tempdir, exist_ok=True)  # NOTE: consider for optimization
        self.request = request
        self.session = request.session

    def preview_url(self, uid):
        return None

    def __contains__(self, name):
        return name in self.session.get(self.session_storage_name, {})

    def __setitem__(self, name, data):
        newdata = data.copy()
        stream = newdata.pop('fp', None)

        if stream is not None:
            newdata['randid'] = uuid4().hex
            with open(os.path.join(self.tempdir, newdata['randid']), 'w+b') as fp:
                shutil.copyfileobj(stream, fp)

        self._tempstore_set(name, newdata)

    def _tempstore_set(self, name, data):
        # cope with sessioning implementations that cant deal with
        # in-place mutation of mutable values (temporarily?)
        existing = self.session.get(self.session_storage_name, {})
        existing[name] = data
        self.session[self.session_storage_name] = existing

    def clear(self):
        data = self.session.pop(self.session_storage_name, {})
        files_to_remove = (
            os.path.join(self.tempdir, v['randid']) for k, v in data.items() if 'randid' in v)
        for fn in files_to_remove:
            try:
                os.remove(fn)
            except OSError:
                pass

    def get(self, name, default=None):
        data = self.session.get(self.session_storage_name, {}).get(name)

        if data is None:
            return default

        newdata = data.copy()

        randid = newdata.get('randid')

        if randid is not None:

            fn = os.path.join(self.tempdir, randid)
            try:
                newdata['fp'] = open(fn, 'rb')
            except IOError:
                pass

        return newdata

    def __getitem__(self, name):
        data = self.get(name, _marker)
        if data is _marker:
            raise KeyError(name)
        return data

