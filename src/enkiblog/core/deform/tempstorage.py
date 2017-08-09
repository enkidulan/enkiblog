import os.path
from uuid import uuid4
import shutil
import logging

logger = logging.getLogger(__name__)

_MARKER = object()


class FileUploadTempStore(object):

    session_storage_slug = 'websauna.tempstore'

    def __init__(self, request):
        self.tempdir = request.registry.settings['websauna.uploads_tempdir']
        if os.path.os.makedirs(self.tempdir, mode=0o777, exist_ok=True):
            logger.warning("Creating dir: '%s'", self.tempdir)
        self.request = request
        self.session = request.session

    def preview_url(self, _uid):
        # pylint: disable=no-self-use
        return None

    def __contains__(self, name):
        return name in self.session.get(self.session_storage_slug, {})

    def __setitem__(self, name, data):
        newdata = data.copy()
        stream = newdata.pop('fp', None)

        if stream is not None:
            newdata['randid'] = uuid4().hex
            file_name = os.path.join(self.tempdir, newdata['randid'])
            shutil.copyfileobj(stream, open(file_name, 'wb'))

        self._tempstore_set(name, newdata)

    def _tempstore_set(self, name, data):
        # cope with sessioning implementations that cant deal with
        # in-place mutation of mutable values (temporarily?)
        existing = self.session.get(self.session_storage_slug, {})
        existing[name] = data
        self.session[self.session_storage_slug] = existing

    def clear(self):
        data = self.session.pop('substanced.tempstore', {})
        for cookie in data.items():
            randid = cookie.get('randid')
            file_name = os.path.join(self.tempdir, randid)
            try:
                os.remove(file_name)
            except OSError:
                pass

    def get(self, name, default=None):
        data = self.session.get(self.session_storage_slug, {}).get(name)

        if data is None:
            return default

        newdata = data.copy()

        randid = newdata.get('randid')

        if randid is not None:

            file_name = os.path.join(self.tempdir, randid)
            try:
                newdata['fp'] = open(file_name, 'rb')
            except IOError:
                pass

        return newdata

    def __getitem__(self, name):
        data = self.get(name, _MARKER)
        if data is _MARKER:
            raise KeyError(name)
        return data
