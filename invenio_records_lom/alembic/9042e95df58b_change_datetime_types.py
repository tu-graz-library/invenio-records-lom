# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2026 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create invenio records lom tables."""

from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "9042e95df58b"
down_revision = "3c1ae3770e92"
branch_labels = ()
depends_on = None


def upgrade() -> None:
    """Upgrade database."""
    for table_name in [
        "lom_parents_metadata",
        "lom_records_metadata",
        "lom_records_metadata_version",
        "lom_drafts_metadata",
        "lom_drafts_files",
        "lom_records_files",
        "lom_records_files_version",
    ]:
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")
    update_table_columns_column_type_to_utc_datetime(
        "lom_drafts_metadata",
        "expires_at",
    )


def downgrade() -> None:
    """Downgrade database."""
    for table_name in [
        "lom_parents_metadata",
        "lom_records_metadata",
        "lom_records_metadata_version",
        "lom_drafts_metadata",
        "lom_drafts_files",
        "lom_records_files",
        "lom_records_files_version",
    ]:
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
    update_table_columns_column_type_to_datetime("lom_drafts_metadata", "expires_at")
