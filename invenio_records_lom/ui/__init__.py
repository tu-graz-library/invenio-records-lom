from flask import Blueprint

from .records import init_records_views


def create_blueprint(app):
    blueprint = Blueprint(
        "invenio_records_lom",
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    init_records_views(blueprint, app)

    return blueprint
