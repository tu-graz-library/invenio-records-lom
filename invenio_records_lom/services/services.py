# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record services configured for LOM-use."""


from invenio_rdm_records.services import RDMRecordService


class LOMRecordService(RDMRecordService):
    """RecordService configured for LOM-use."""
