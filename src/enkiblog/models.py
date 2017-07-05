"""
ORM models form enkiblog
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql_dialect

from enkiblog.core.models import BaseResourceMixin, ContentResourceMixin, UUID

# pylint: disable=too-few-public-methods


class AssociationPostsTags:
    """
    Association Table to keep relations between model, in perspective will evolve
    into taxonomy
    """
    __tablename__ = "association_posts_tags"
    post_uuid = sa.Column(UUID(), sa.ForeignKey('posts.uuid'), primary_key=True)
    tag_uuid = sa.Column(UUID(), sa.ForeignKey('tags.uuid'), primary_key=True)


class Post(ContentResourceMixin):
    """
    Model for post content object
    """
    __tablename__ = "posts"

    body = sa.Column(sa.Text(), nullable=False, default="")

    tags = sa.orm.relationship(
        'Tag', secondary=AssociationPostsTags.__tablename__, back_populates="posts")


class Media(ContentResourceMixin):
    """
    Media resource model, work for all file-alike resources
    """
    __tablename__ = "media"
    # IDEA: add relation to linked resource for tracking
    # IDEA: make referenced ACL - get acl from parent object

    mimetype = sa.Column(sa.String(256), default="")

    # NOTE: in general keep binaries in DB is not the best idea, but I want to
    #       simplify maintenance cost and know for sure that there will be only
    #       few small media object
    blob = sa.Column(psql_dialect.BYTEA)


class Tag(BaseResourceMixin):
    """
    Tag resource model, basic taxonomy realization for now
    """
    __tablename__ = "tags"

    posts = sa.orm.relationship(
        'Post', secondary=AssociationPostsTags.__tablename__, back_populates="tags")


def includeme(config):  # pylint: disable=unused-argument
    """ Attaching all declared models to Base here """
    from websauna.system.model.meta import Base
    from websauna.system.model.utils import attach_model_to_base

    # IDEA: make it dynamic, kind of as if it were inherited from Base model, but provide
    #       app registry in  meta
    attach_model_to_base(Post, Base)
    attach_model_to_base(AssociationPostsTags, Base)
    attach_model_to_base(Media, Base)
    attach_model_to_base(Tag, Base)
