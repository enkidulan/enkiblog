from websauna.system.core.views.notfound import notfound
from pyramid.view import view_config


@view_config(route_name='register')
@view_config(route_name='activate')
@view_config(route_name='registration_complete')
@view_config(route_name='forgot_password')
@view_config(route_name='reset_password')
def terminator(request):  # so far don't want to have any registration on site
    return notfound(request)
