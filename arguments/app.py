import logging
import os
import jinja2
from more.transaction import TransactionApp
from morepath.reify import reify
from morepath.request import Request
import morepath
import yaml

from arguments.helper.templating import make_jinja_env
from arguments import database


logg = logging.getLogger(__name__)


class CustomRequest(Request):
    
    @reify
    def db_session(self): 
        return database.Session()

    def q(self, *args, **kwargs):
        return self.db_session.query(*args, **kwargs)

    def render_template(self, template, **context):
        template = self.app.jinja_env.get_template(template)
        return template.render(**context)


class App(TransactionApp):
    request_class = CustomRequest
    
    def __init__(self):
        super().__init__()
        template_loader = jinja2.PackageLoader("arguments")
        self.jinja_env = make_jinja_env(jinja_environment_class=jinja2.Environment, jinja_options=dict(loader=template_loader))


def get_app_settings(settings_filepath):
    from arguments.default_settings import settings

    if settings_filepath is None:
        logg.info("no config file given")
    elif os.path.isfile(settings_filepath):
        with open(settings_filepath) as config:
            settings_from_file = yaml.load(config)
        logg.info("loaded config from %s", settings_filepath)

        for section_name, section in settings_from_file.items():
            if section_name in settings:
                settings[section_name].update(section)
            else:
                settings[section_name] = section
    else:
        logg.warn("config file path %s doesn't exist!")

    return settings


def make_wsgi_app(args):
    morepath.autoscan()
    settings = get_app_settings(args.config_file)
    App.init_settings(settings)
    App.commit()

    app = App()
    database.configure_sqlalchemy(app.settings.database)
    return app
