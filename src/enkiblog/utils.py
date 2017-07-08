"""  Wildly used or units that is doesn't belong to other modules goes here """
from slugify import slugify as base_slugify


def get_alcheme_max_length(field):
    """ Returns sqlacheme field max length """
    try:
        return getattr(field.class_.__table__.c, field.key).type.length
    except AttributeError:
        pass


def is_field_value_unique(dbsession, field, slug):
    """ check in db if record with same slug already exists or not"""
    return dbsession.query(field.class_).filter(field == slug).one_or_none() is None


def slugify(
        text,
        field,
        dbsession,
        get_max_length=get_alcheme_max_length,
        validate_field_value_uniqueness=is_field_value_unique):
    """
    creates a slug for a model, guaranties slug uniqueness
    and resolves collisions by adding increment suffix
    """
    for i in range(99):
        unifier = str(i)
        slug = base_slugify(text, max_length=get_max_length(field) - len(unifier))
        slug += unifier if i else ''
        if validate_field_value_uniqueness(dbsession, field, slug):
            break
    else:
        raise RuntimeError('Wasn\'t able to generate slug')
    return slug
