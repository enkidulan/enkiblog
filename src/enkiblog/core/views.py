import os.path
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.events import subscriber
from sqlalchemy.orm.exc import NoResultFound
from websauna.system.core.views.notfound import notfound
from websauna.system.core.events import InternalServerError
from websauna.system.core.loggingcapture import get_logging_user_context


_icon = open(os.path.join(os.path.dirname(__file__), 'static', 'favicon.ico'), 'rb').read()
_fi_response = Response(content_type='image/x-icon', body=_icon)


@view_config(name='favicon.ico')
def favicon_view(context, request):
    """ favicon serving view """
    return _fi_response


@view_config(context=NoResultFound)
def failed_validation(exc, request):
    return notfound(request)


# TODO: not found return and not raise found leads to different pages - fix that

# https://github.com/websauna/websauna.sentry/blob/master/websauna/sentry/subscribers.py#L14
@subscriber(InternalServerError)
def notify_raven(event):
    request = event.request
    user_context = get_logging_user_context(request)
    request.raven.user_context(user_context)
    request.raven.captureException()
