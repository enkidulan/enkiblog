import os.path
from uuid import uuid4
import shutil
import logging
log = logging.getLogger(__name__)

_marker = object()


class FileUploadTempStore(object):

    session_storage_slug = 'websauna.tempstore'

    def __init__(self, request):
        self.tempdir = request.registry.settings['websauna.uploads_tempdir']
        if os.path.os.makedirs(self.tempdir, mode=0o777, exist_ok=True):
            log.warn("Creating dir: '%s'", self.tempdir)
        self.request = request
        self.session = request.session

    def preview_url(self, uid):
        return None

    def __contains__(self, name):
        return name in self.session.get(self.session_storage_slug, {})

    def __setitem__(self, name, data):
        newdata = data.copy()
        stream = newdata.pop('fp', None)

        if stream is not None:
            newdata['randid'] = uuid4().hex
            fn = os.path.join(self.tempdir, newdata['randid'])
            shutil.copyfileobj(stream, open(fn, 'wb'))

        self._tempstore_set(name, newdata)

    def _tempstore_set(self, name, data):
        # cope with sessioning implementations that cant deal with
        # in-place mutation of mutable values (temporarily?)
        existing = self.session.get(self.session_storage_slug, {})
        existing[name] = data
        self.session[self.session_storage_slug] = existing

    def clear(self):
        data = self.session.pop('substanced.tempstore', {})
        for v in data.items():
            randid = v.get('randid')
            fn = os.path.join(self.tempdir, randid)
            try:
                os.remove(fn)
            except OSError:
                pass

    def get(self, name, default=None):
        data = self.session.get(self.session_storage_slug, {}).get(name)

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
