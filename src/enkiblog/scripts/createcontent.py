"""ws-create-user - creating users from command line."""
import random
import sys

from websauna.system.devop.cmdline import init_websauna
from websauna.system.user.events import UserCreated
from websauna.system.user.models import Group
from websauna.system.user.utils import get_user_class, get_user_registry
from websauna.utils.time import now

from enkiblog.core.testing import fakefactory as base_fakefactory
from enkiblog.tests import fakefactory


def get_or_create_user(request, email, password):
    User = get_user_class(request.registry)
    dbsession = request.dbsession

    u = dbsession.query(User).filter_by(email=email).first()
    if u is not None:
        return u

    u = User(email=email, username=email)
    dbsession.add(u)
    dbsession.flush()  # Make sure u.user_data is set

    if password:
        user_registry = get_user_registry(request)
        user_registry.set_password(u, password)

    u.registration_source = "command_line"
    u.activated_at = now()

    request.registry.notify(UserCreated(request, u))

    return u


def main(argv=sys.argv):
    size = 200
    tags_rel_min = 5
    tags_rel_max = 30

    config_uri = argv[1]

    request = init_websauna(config_uri)
    base_fakefactory.DB_SESSION_PROXY.session = request.dbsession

    with request.tm:
        user = get_or_create_user(request, email="user@foo.bar", password="qwerty")
        tags = fakefactory.TagFactory.create_batch(size=size)
        posts = fakefactory.PostFactory.create_batch(
            size=size,
            author=user,
            tags=random.sample(tags, k=random.randint(tags_rel_min, tags_rel_max)),
        )


if __name__ == "__main__":
    main()
