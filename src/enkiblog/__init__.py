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
        super().configure_static()
        # custom widget static view
        self.static_asset_policy.add_static_view(
            'deform-custom-widget-static', 'enkiblog.core.deform.widgets:static')
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
        # We override this method, so that we route home to our home
        # screen, not Websauna default one
        self.config.add_route('home', '/')
        self.config.add_route(
            'old_post', '/programming/notes-on-web-development-with-python/{slug}')
        self.config.add_route('post', '/programming/{slug}')
        self.config.add_route('media', '/media/{slug}')

        from . import views
        self.config.scan(views)

    def configure_models(self):
        from . import models
        self.config.scan(models)

    def configure_model_admins(self):
        # Call parent which registers user and group admins
        super().configure_model_admins()

        # Scan our admins
        from . import admins
        self.config.scan(admins)
        from . import adminviews
        self.config.scan(adminviews)

    def create_static_asset_policy(self):
        import pkg_resources
        from enkiblog.core.static import RevisionBasedStaticAssetPolicy

        revision = pkg_resources.get_distribution("enkiblog").version
        return RevisionBasedStaticAssetPolicy(revision, self.config)

    def configure_forms(self):
        super().configure_forms()

        # from websauna.system.form.resources import DefaultFormResources
        from websauna.system.form.interfaces import IFormResources
        from websauna.system.form.deform import configure_zpt_renderer

        # Make Deform widgets aware of our widget template paths
        configure_zpt_renderer(["enkiblog.core.deform.widgets:templates"])
        form_resources = self.config.registry.getUtility(IFormResources).get_default_resources()
        form_resources['ckeditor'] = {None: {
            'js': 'enkiblog.core.deform.widgets:static/ckeditor/ckeditor.js',
            'css': 'enkiblog.core.deform.widgets:static/ckeditor/contents.css',
        }}

    def make_overrides(self):
        self.config.commit()  # there is views overrides in overrides.py
        from . import overrides
        self.config.scan(overrides)

        from enkiblog.core.authorization import ContextualACLAuthorizationPolicy
        authz_policy = ContextualACLAuthorizationPolicy()
        self.config.set_authorization_policy(authz_policy)

    def configure_database(self):
        from websauna.system.model.meta import get_engine
        from enkiblog.core.meta import create_session_maker
        engine = get_engine(self.config.registry.settings)
        self.config.registry.db_session_maker = create_session_maker(engine)
        super().configure_database()

    def include_addons(self):
        super().include_addons()
        self.config.include('pyramid_layout')
        self.config.include('pyramid_mako')
        self.config.include('pyramid_chameleon')
        self.config.include('pyramid_raven')

    def run(self):
        super().run()
        self.configure_workflow()
        self.make_overrides()


def main(global_config, **settings):  # pylint: disable=unused-argument
    init = Initializer(global_config)
    init.run()
    return init.make_wsgi_app()
