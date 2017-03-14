"""App entry point and configuration."""
from functools import partial
import websauna.system


class Initializer(websauna.system.Initializer):
    """An initialization configuration used for starting enkiblog.

    Override parent class methods to customize application behavior.
    """

    def configure_static(self):
        """Configure static asset serving and cache busting."""
        super(Initializer, self).configure_static()

        self.config.registry.static_asset_policy.add_static_view('enkiblog-static', 'enkiblog:static')

    def configure_templates(self):
        """Include our package templates folder in Jinja 2 configuration."""
        super(Initializer, self).configure_templates()
        search_templates = partial(
            self.config.add_jinja2_search_path, 'enkiblog:templates', prepend=True)

        search_templates(name='.html')  # HTML templates for pages
        search_templates(name='.txt')  # Plain text email templates (if any)
        search_templates(name='.xml')  # Sitemap and misc XML files (if any)

    def configure_views(self):
        """Configure views for your application.

        Let the config scanner to pick ``@simple_route`` definitions from scanned modules. Alternative you can call ``config.add_route()`` and ``config.add_view()`` here.
        """
        # We override this method, so that we route home to our home screen, not Websauna default one
        self.config.add_route('home', '/')
        self.config.add_route('posts', '/posts/{slug}')
        from . import views
        self.config.scan(views)

    def configure_models(self):
        """Register the models of this application."""
        from . import models
        self.config.scan(models)

    def configure_model_admins(self):
        """Register the models of this application."""

        # Call parent which registers user and group admins
        super(Initializer, self).configure_model_admins()

        # Scan our admins
        from . import admins
        self.config.scan(admins)
        from . import adminviews
        self.config.scan(adminviews)

    # def configure_database(self):
    #     """Configure database.

    #     * Set up base model

    #     * Set up mechanism to create database session for requests

    #     * Set up transaction machinery

    #     Calls py:func:`websauna.system.model.meta.includeme`.

    #     """
    #     # super().configure_database()

    #     self.config.include("pyramid_tm")
    #     self.config.include(".model.meta")
    #     from pyramid.interfaces import IRequest
    #     from websauna.system.model.interfaces import ISQLAlchemySessionFactory
    #     from enkiblog.tests.fakefactory import create_test_dbsession

    #     self.config.registry.registerAdapter(
    #         factory=create_test_dbsession,
    #         required=(IRequest,),
    #         provided=ISQLAlchemySessionFactory)

    def run(self):
        super(Initializer, self).run()


def main(global_config, **settings):
    init = Initializer(global_config)
    init.run()
    return init.make_wsgi_app()
