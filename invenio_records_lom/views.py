from flask import Blueprint

blueprint = Blueprint("invenio_records_lom_ext", __name__)


@blueprint.record_once
def init(state):
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    registry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-records-lom"]

    registry.register(ext.records_service, service_id="lom-records")
    registry.register(ext.records_service.files, service_id="lom-files")
    registry.register(ext.records_service.draft_files, service_id="lom-draft-files")


def create_records_bp(app):
    """Create records blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()


def create_record_files_bp(app):
    """Create records files blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()
    return ext.record_files_resource.as_blueprint()


def create_draft_files_bp(app):
    """Create draft files blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()
    return ext.draft_files_resource.as_blueprint()


def create_parent_record_links_bp(app):
    """Create parent record links blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()
    return ext.parent_record_links_resource.as_blueprint()
