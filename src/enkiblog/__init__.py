"""App entry point and configuration."""
from functools import partial
import websauna.system


class Initializer(websauna.system.Initializer):
    """An initialization configuration used for starting enkiblog.

    Override parent class methods to customize application behavior.
    """

    def configure_workflow(self):
        """Configure workflow."""
        from . import workflow
        self.config.include(workflow)

    def configure_static(self):
        """Configure static asset serving and cache busting."""
        super(Initializer, self).configure_static()
        # custom widget static view
        self.static_asset_policy.add_static_view('deform-custom-widget-static', 'enkiblog.deform_widgets:static')
        self.static_asset_policy.add_static_view('enkiblog-static', 'enkiblog:static')

    def configure_templates(self):
        """Include our package templates folder in Jinja 2 configuration."""
        super(Initializer, self).configure_templates()
        search_templates = partial(
            self.config.add_jinja2_search_path, 'enkiblog:templates', prepend=True)

        search_templates(name='.html')  # HTML templates for pages
        search_templates(name='.txt')  # Plain text email templates (if any)
        search_templates(name='.xml')  # Sitemap and misc XML files (if any)

    def configure_views(self):
        # We override this method, so that we route home to our home screen, not Websauna default one
        self.config.add_route('home', '/')
        self.config.add_route('post', '/programming/{slug}')
        self.config.add_route('media', '/media/{slug}')
        from . import views
        self.config.scan(views)

    def configure_models(self):
        from . import models
        self.config.scan(models)

    def configure_model_admins(self):
        # Call parent which registers user and group admins
        super(Initializer, self).configure_model_admins()

        # Scan our admins
        from . import admins
        self.config.scan(admins)
        from . import adminviews
        self.config.scan(adminviews)

    def create_static_asset_policy(self):
        from websauna.system.http.static import StaticAssetPolicy
        from pyramid.static import QueryStringConstantCacheBuster

        class SimpleStaticAssetPolicy(StaticAssetPolicy):
            static_version = '2017-05-30'  # TODO: that is stupid - replace with release number or calculate dynamically
            def add_static_view(self, name: str, path: str):
                cache_max_age = self.config.registry.settings.get("websauna.cache_max_age_seconds")
                if cache_max_age:
                    cache_max_age = int(cache_max_age)
                self.config.add_static_view(name, path, cache_max_age=cache_max_age)
                if cache_max_age:
                    self.config.add_cache_buster(
                        path, QueryStringConstantCacheBuster(self.static_version))
        return SimpleStaticAssetPolicy(self.config)

    def configure_forms(self):
        super().configure_forms()

        # from websauna.system.form.resources import DefaultFormResources
        from websauna.system.form.interfaces import IFormResources
        from websauna.system.form.deform import configure_zpt_renderer

        # Make Deform widgets aware of our widget template paths
        configure_zpt_renderer(["enkiblog.deform_widgets:templates"])
        form_resources = self.config.registry.getUtility(IFormResources).get_default_resources()
        form_resources['ckeditor'] = {None: {
            'js': 'enkiblog.deform_widgets:static/ckeditor/ckeditor.js',
            'css': 'enkiblog.deform_widgets:static/ckeditor/contents.css',
        }}

    def run(self):
        self.configure_workflow()
        super(Initializer, self).run()


def main(global_config, **settings):
    init = Initializer(global_config)
    init.run()
    return init.make_wsgi_app()
