from websauna.system.admin import views as adminviews
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing

from enkiblog.admins import TagAdmin
from enkiblog.models import AssociationPostsTags


def get_references_count(view, column, obj):
    count = view.request.dbsession.query(AssociationPostsTags).filter(
        AssociationPostsTags.tag_uuid == obj.uuid).count()
    return count


@view_overrides(context=TagAdmin)
class TagsListing(adminviews.Listing):

    table = listing.Table(
        columns=[
            listing.Column("title", "Title"),
            listing.Column("references_count", "References Count", getter=get_references_count),
            listing.ControlsColumn(),
        ]
    )
