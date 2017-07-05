"""App entry point and configuration."""
from functools import partial
import websauna.system
from pkg_resources import get_distribution

__version__ = get_distribution('enkiblog').version


class Initializer(websauna.system.Initializer):
    """
    An initialization configuration used for starting enkiblog.
    Override parent class methods to customize application behavior.
    """

    def configure_workflow(self):
        """Configure workflow."""
        from . import workflow
        self.config.include(workflow)

    def configure_static(self):
        """Configure static asset serving and cache busting."""
        super().configure_static()
        # custom widget static view
        self.static_asset_policy.add_static_view(
            'deform-custom-widget-static', 'enkiblog.deform_widgets:static')
        self.static_asset_policy.add_static_view('enkiblog-static', 'enkiblog:static')

    def configure_templates(self):
        """Include our package templates folder in Jinja 2 configuration."""
        super().configure_templates()
        add_templates = partial(
            self.config.add_jinja2_search_path, 'enkiblog:templates', prepend=True)

        add_templates(name='.html')  # HTML templates for pages
        add_templates(name='.txt')  # Plain text email templates (if any)
        add_templates(name='.xml')  # Sitemap and misc XML files (if any)

    def configure_views(self):
        """Views configuration"""
        self.config.add_route('home', '/')
        self.config.add_route(
            'old_post', '/programming/notes-on-web-development-with-python/{slug}')
        self.config.add_route('post', '/programming/{slug}')
        self.config.add_route('media', '/media/{slug}')

        from . import views
        self.config.scan(views)

    def configure_instrumented_models(self):
        super().configure_instrumented_models()
        from . import models
        self.config.include(models)

    # def configure_models(self):
    #     """Models configuration"""
    #     super().configure_models()

    #     # self.config.scan(models)

    def configure_model_admins(self):
        """Admin Models configuration"""

        # Call parent which registers user and group admins
        super().configure_model_admins()

        # Scan our admins
        from . import admins
        self.config.scan(admins)
        from . import adminviews
        self.config.scan(adminviews)

    def create_static_asset_policy(self):
        """
        Static Assets Policy configuration.
        Default one wasn't compatible with modern JS frameworks/libs
        """
        from websauna.system.http.static import StaticAssetPolicy
        from pyramid.static import QueryStringConstantCacheBuster

        # pylint: disable=too-few-public-methods
        class SimpleStaticAssetPolicy(StaticAssetPolicy):
            """
            Static Asset Policy with custom simple cache buster
            based on package version.
            """
            static_version = __version__

            def add_static_view(self, name: str, path: str):
                """ Adds static view and sets cache buster for it"""
                cache_max_age = self.config.registry.settings.get(
                    "websauna.cache_max_age_seconds")
                if cache_max_age:
                    cache_max_age = int(cache_max_age)
                self.config.add_static_view(name, path, cache_max_age=cache_max_age)
                if cache_max_age:
                    self.config.add_cache_buster(
                        path, QueryStringConstantCacheBuster(self.static_version))

        return SimpleStaticAssetPolicy(self.config)

    def configure_forms(self):
        """Forms configuration"""

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

    def make_overrides(self):
        """
        Overrides configuration step that runs after all other configuration steps,
        put in there things that is needed to be overrider in config
        """
        self.config.commit()

        from . import overrides
        self.config.scan(overrides)

        # original ACLAuthorizationPolicy wasn't enough
        from enkiblog.authorization import ContextualACLAuthorizationPolicy
        authz_policy = ContextualACLAuthorizationPolicy()
        self.config.set_authorization_policy(authz_policy)

    def configure_database(self):
        """Database configuration"""

        from websauna.system.model.meta import get_engine
        from enkiblog.meta import create_session_maker
        engine = get_engine(self.config.registry.settings)
        self.config.registry.db_session_maker = create_session_maker(engine)
        super().configure_database()

    def include_addons(self):
        """Addons including/configuration"""

        super().include_addons()
        self.config.include('pyramid_layout')
        self.config.include('pyramid_mako')
        self.config.include('pyramid_chameleon')
        self.config.include('pyramid_raven')

    def run(self):
        """Configuration runner"""
        self.configure_workflow()
        super().run()
        self.make_overrides()


def main(global_config, **_):
    """Main wsgi making app"""
    init = Initializer(global_config)
    init.run()
    return init.make_wsgi_app()
