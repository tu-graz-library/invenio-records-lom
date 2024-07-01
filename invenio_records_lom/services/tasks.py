# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for LOM module."""


from datetime import datetime, timedelta, timezone

from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_search.engine import dsl
from invenio_search.proxies import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats.bookmark import BookmarkAPI

from ..proxies import current_records_lom


@shared_task(ignore_result=True)
def register_or_update_pid(recid: str, scheme: str) -> None:
    """Update PID on remote providers."""
    current_records_lom.records_service.pids.register_or_update(
        id_=recid,
        identity=system_identity,
        scheme=scheme,
    )


@shared_task(ignore_result=True)
def lom_reindex_stats(stats_indices: list) -> str:
    """Reindex the documents where the stats have changed."""
    bm = BookmarkAPI(current_search_client, "lom_stats_reindex", "day")
    last_run = bm.get_bookmark()
    if not last_run:
        # If this is the first time that we run, let's do it for the documents
        # of the last week
        last_run = (datetime.now(timezone.UTC) - timedelta(days=7)).isoformat()

    reindex_start_time = datetime.now(timezone.UTC).isoformat()
    indices = ",".join(f"{prefix_index(x)}*" for x in stats_indices)

    all_parents = set()
    query = dsl.Search(
        using=current_search_client,
        index=indices,
    ).filter({"range": {"updated_timestamp": {"gte": last_run}}})

    for result in query.scan():
        parent_id = result.parent_recid
        all_parents.add(parent_id)

    if all_parents:
        all_parents_list = list(all_parents)
        step = 10000
        end = len(list(all_parents))
        for i in range(0, end, step):
            records_q = dsl.Q("terms", parent__id=all_parents_list[i : i + step])
            current_records_lom.records_service.reindex(
                params={"allversions": True},
                identity=system_identity,
                search_query=records_q,
            )
    bm.set_bookmark(reindex_start_time)
    return f"{len(all_parents)} documents reindexed"
