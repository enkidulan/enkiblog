from slugify import slugify as base_slugify


def get_max_length(field):
    try:
        return getattr(field.class_.__table__.c, field.key).type.length
    except AttributeError:
        pass


def is_slug_already_exists(dbsession, field, slug):
    return dbsession.query(field.class_).filter(field == slug).one_or_none() is None


def slugify(text, field, dbsession, get_max_length=get_max_length, is_slug_already_exists=is_slug_already_exists):
    for i in range(99):
        unifier = str(i)
        slug = base_slugify(text, max_length=get_max_length(field) - len(unifier))
        slug += unifier if i else ''
        if is_slug_already_exists(dbsession, field, slug):
            break
    else:
        raise RuntimeError('Wasn\'t able to generate slug')
    return slug
