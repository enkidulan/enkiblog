from collections import namedtuple
import factory
from pyramid.threadlocal import get_current_registry

from websauna.system.user import models as ws_models
from websauna.system.user.interfaces import IPasswordHasher
from websauna.utils.time import now

from enkiblog import models
from enkiblog.utils import slugify


class DBSessionProxy:
    session = None

    def __getattr__(self, attr):
        return getattr(self.session, attr)


db_session_proxy = DBSessionProxy()


def hash_password(password):
    # ???: should I pass "registry" trougth proxy as well?
    registry = get_current_registry()
    hasher = registry.getUtility(IPasswordHasher)
    hashed = hasher.hash_password(password)
    return hashed


def ensure_admin_group_returned():
    admin_group = db_session_proxy.query(ws_models.Group).filter_by(
        name=ws_models.Group.DEFAULT_ADMIN_GROUP_NAME).first()
    if admin_group is None:
        admin_group = GroupFactory(name=ws_models.Group.DEFAULT_ADMIN_GROUP_NAME)
    return admin_group


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        sqlalchemy_session = db_session_proxy
        force_flush = True
        abstract = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        excluded = {k: w for k, w in kwargs.items() if k in cls._meta.exclude}
        obj = super()._prepare(create, **kwargs)
        obj._fb_excluded = namedtuple('excluded', excluded)(**excluded)
        return obj


class GroupFactory(BaseFactory):
    class Meta:
        model = ws_models.Group

    name = factory.Faker('slug')


class UserFactory(BaseFactory):
    class Meta:
        model = ws_models.User
        exclude = ('password',)

    class Params:
        password = factory.Faker('slug')

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    # role = 'no roles yet'
    hashed_password = factory.LazyAttribute(lambda obj: hash_password(obj.password))
    activated_at = factory.LazyAttribute(lambda obj: now())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = super()._create(model_class, *args, **kwargs)
        assert user.can_login()
        return user


class AdminFactory(UserFactory):

    groups = factory.LazyAttribute(lambda obj: [ensure_admin_group_returned()])


class BasePostFactory(BaseFactory):
    class Meta:
        model = models.Post

    title = factory.Faker('catch_phrase')
    description = factory.Faker('text')
    body = factory.Faker('paragraphs')
    slug = factory.LazyAttribute(
        lambda obj: slugify(obj.title, models.Post.slug, db_session_proxy))


class PostFactory(BasePostFactory):
    state = 'published'
    published_at = factory.LazyAttribute(lambda obj: now())
