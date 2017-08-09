import os.path
from random import randint
from uuid import uuid4

import factory
from websauna.utils.time import now

from enkiblog import models
from enkiblog.core.utils import slugify
from enkiblog.core.testing.fakefactory import BaseFactory, DB_SESSION_PROXY

# pylint: disable=unused-wildcard-import
# NOTE: HACK to have all factories in one fixture
# ???: Do I need it to have all factories in one fixture?
from enkiblog.core.testing.fakefactory import *


class BasePostFactory(BaseFactory):
    class Meta:
        model = models.Post

    title = factory.Faker('catch_phrase')
    description = factory.Faker('text')
    body = factory.Faker('text')
    slug = factory.LazyAttribute(
        lambda obj: slugify(obj.title, models.Post.slug, DB_SESSION_PROXY))
    tags = factory.LazyFunction(lambda: [TagFactory() for i in range(randint(1, 6))])


class PostFactory(BasePostFactory):
    state = 'public'
    published_at = factory.LazyAttribute(lambda obj: now())


class TagFactory(BaseFactory):
    class Meta:
        model = models.Tag

    # title = factory.Faker('word')
    title = factory.LazyAttribute(lambda obj: str(uuid4().hex))  # XXX: !!! see previous


class MediaFactory(BaseFactory):
    class Meta:
        model = models.Media

    # XXX: will break in case of many files
    description = factory.Faker('slug')
    title = str(__file__.rsplit(os.path.sep, 1)[-1])
    slug = factory.Faker('slug')
    blob = bytes(os.path.abspath(__file__), 'utf-8')
