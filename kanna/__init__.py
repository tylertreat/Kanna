"""Create a flask app blueprint."""

import furious_router
furious_router.setup_lib_path()

import flask

from kanna.view.blueprint import blueprint as view_blueprint

# Imported to register urls
from kanna.view import views


def create_app(config="kanna.settings"):
    app = flask.Flask(__name__, template_folder='../templates')

    app.config.from_object(config)

    app.register_blueprint(view_blueprint)

    # Enable jinja2 loop controls extension
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    return app

