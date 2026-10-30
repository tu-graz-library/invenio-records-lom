# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Create invenio records lom branch."""

# revision identifiers, used by Alembic.
revision = "84003810e5b1"
down_revision = None
branch_labels = ("invenio_records_lom",)
depends_on = "dbdbc1b19cf2"


def upgrade() -> None:
    """Upgrade database."""


def downgrade() -> None:
    """Downgrade database."""
