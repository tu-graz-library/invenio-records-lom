# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create invenio records lom tables."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3c1ae3770e92"
down_revision = "1dc5abf0e34b"
branch_labels = ()
depends_on = None


def upgrade() -> None:
    """Upgrade database."""
    # step 1: create the columns, but make them nullable for now
    op.add_column(
        "lom_records_metadata",
        sa.Column("deletion_status", sa.String(length=1), nullable=True),
    )
    op.add_column(
        "lom_records_metadata_version",
        sa.Column(
            "deletion_status",
            sa.String(length=1),
            nullable=True,
        ),
    )

    # step 2: set default values for existing rows
    default_value = "P"
    metadata_table = sa.sql.table(
        "lom_records_metadata",
        sa.sql.column("deletion_status"),
    )
    metadata_version_table = sa.sql.table(
        "lom_records_metadata_version",
        sa.sql.column("deletion_status"),
    )
    op.execute(metadata_table.update().values(deletion_status=default_value))
    op.execute(metadata_version_table.update().values(deletion_status=default_value))

    # step 3: make the original table not nullable
    op.alter_column("lom_records_metadata", "deletion_status", nullable=False)


def downgrade() -> None:
    """Downgrade database."""
    op.drop_column("lom_records_metadata_version", "deletion_status")
    op.drop_column("lom_records_metadata", "deletion_status")
