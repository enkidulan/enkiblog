# pylint: disable=too-few-public-methods
from enkiblog import models
import os.path
from websauna.utils.time import now
from random import randint
from uuid import uuid4

import factory

from enkiblog.core.utils import slugify
from enkiblog.core.testing.fakefactory import BaseFactory, DB_SESSION_PROXY


class TagFactory(BaseFactory):
    class Meta:
        model = models.Tag

    # title = factory.Faker('words', )
    title = factory.LazyAttribute(lambda obj: str(uuid4().hex))  # XXX: !!! see previous


class BasePostFactory(BaseFactory):
    class Meta:
        model = models.Post

    title = factory.Faker('catch_phrase')
    description = factory.Faker('sentence')
    body = factory.Faker('text', max_nb_chars=2000)
    slug = factory.LazyAttribute(
        lambda obj: slugify(obj.title, models.Post.slug, DB_SESSION_PROXY))
    tags = factory.LazyFunction(lambda: [TagFactory() for i in range(randint(1, 6))])


class PostFactory(BasePostFactory):
    state = 'public'
    published_at = factory.LazyAttribute(lambda obj: now())


class MediaFactory(BaseFactory):
    class Meta:
        model = models.Media

    # XXX: will break in case of many files
    description = factory.Faker('slug')
    title = str(__file__.rsplit(os.path.sep, 1)[-1])
    slug = factory.Faker('slug')
    blob = bytes(os.path.abspath(__file__), 'utf-8')
