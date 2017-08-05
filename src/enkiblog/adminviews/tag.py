from websauna.system.admin import views as adminviews
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing
from enkiblog.admins import TagAdmin


@view_overrides(context=TagAdmin)
class TagsListing(adminviews.Listing):

    table = listing.Table(
        columns=[
            listing.Column("title", "Title"),
            listing.ControlsColumn(),
        ]
    )

    def order_query(self, query):
        """Sort the query."""
        return query.order_by('title')
