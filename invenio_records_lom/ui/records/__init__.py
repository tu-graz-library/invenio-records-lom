from invenio_app_rdm.records_ui.views import (
    not_found_error,
    pid_url,
    record_permission_denied_error,
    record_tombstone_error,
)
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDUnregistered,
)
from invenio_records_resources.services.errors import PermissionDeniedError

from .records import (
    record_detail,
    record_export,
    record_file_download,
    record_file_preview,
)


def init_records_views(blueprint, app):
    routes = app.config["LOM_ROUTES"]

    blueprint.add_url_rule(
        routes["record_detail"],
        view_func=record_detail,
    )
    blueprint.add_url_rule(
        routes["record_export"],
        view_func=record_export,
    )
    blueprint.add_url_rule(
        routes["record_file_preview"],
        view_func=record_file_preview,
    )
    blueprint.add_url_rule(
        routes["record_file_download"],
        view_func=record_file_download,
    )

    # Register error handlers
    blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)
    blueprint.register_error_handler(PIDUnregistered, not_found_error)
    blueprint.register_error_handler(KeyError, not_found_error)
    blueprint.register_error_handler(
        PermissionDeniedError, record_permission_denied_error
    )

    # Register template filters
    blueprint.add_app_template_filter(pid_url)
