from pyramid.static import QueryStringConstantCacheBuster
from websauna.system.http.static import StaticAssetPolicy


# pylint: disable=too-few-public-methods
class RevisionBasedStaticAssetPolicy(StaticAssetPolicy):

    def __init__(self, revision, *args, **kwargs):
        self.revision = str(revision)
        super().__init__(*args, **kwargs)

    def add_static_view(self, name: str, path: str):
        cache_max_age = self.config.registry.settings.get("websauna.cache_max_age_seconds")
        if cache_max_age:
            cache_max_age = int(cache_max_age)
        self.config.add_static_view(name, path, cache_max_age=cache_max_age)
        if cache_max_age:
            self.config.add_cache_buster(
                path, QueryStringConstantCacheBuster(self.revision))
