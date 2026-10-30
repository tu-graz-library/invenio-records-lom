# SPDX-FileCopyrightText: 2020-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Submodule for creating demo records."""

from .demo import (
    create_fake_data,
    publish_fake_record,
    publish_fake_record_over_celery,
    publish_fake_records,
)

__all__ = (
    "create_fake_data",
    "publish_fake_record",
    "publish_fake_record_over_celery",
    "publish_fake_records",
)
