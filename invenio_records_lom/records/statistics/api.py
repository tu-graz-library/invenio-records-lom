# SPDX-FileCopyrightText: 2019 CERN.
# SPDX-FileCopyrightText: 2022 TU Wien.
# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Permission factories for invenio-records-lom.

In contrast to the very liberal defaults provided by
invenio-records-lom, these permission factories deny access unless
otherwise specified.
"""

from flask import current_app
from invenio_rdm_records.records.stats import Statistics


class LomStatistics(Statistics):
    """Lom statistics API class."""

    prefix = "lom-record"

    @classmethod
    def get_record_stats(cls, recid: str, parent_recid: str) -> dict:
        """Fetch the statistics for the given record."""
        try:
            views = cls._get_query(f"{cls.prefix}-view").run(recid=recid)
            views_all = cls._get_query(f"{cls.prefix}-view-all-versions").run(
                parent_recid=parent_recid,
            )
        except Exception as e:  # noqa: BLE001
            # e.g. opensearchpy.exceptions.NotFoundError
            # when the aggregation search index hasn't been created yet
            current_app.logger.warning(e)

            fallback_result = {
                "views": 0,
                "unique_views": 0,
            }
            views = views_all = downloads = downloads_all = fallback_result

        try:
            downloads = cls._get_query(f"{cls.prefix}-download").run(recid=recid)
            downloads_all = cls._get_query(f"{cls.prefix}-download-all-versions").run(
                parent_recid=parent_recid,
            )
        except Exception as e:  # noqa: BLE001
            # same as above, but for failure in the download statistics
            # because they are a separate index that can fail independently
            current_app.logger.warning(e)

            fallback_result = {
                "downloads": 0,
                "unique_downloads": 0,
                "data_volume": 0,
            }
            downloads = downloads_all = fallback_result

        return {
            "this_version": {
                "views": views["views"],
                "unique_views": views["unique_views"],
                "downloads": downloads["downloads"],
                "unique_downloads": downloads["unique_downloads"],
                "data_volume": downloads["data_volume"],
            },
            "all_versions": {
                "views": views_all["views"],
                "unique_views": views_all["unique_views"],
                "downloads": downloads_all["downloads"],
                "unique_downloads": downloads_all["unique_downloads"],
                "data_volume": downloads_all["data_volume"],
            },
        }
