from invenio_rdm_records.resources.serializers import UIJSONSerializer

from .schema import LOMUIObjectSchema


class LOMUIJSONSerializer(UIJSONSerializer):
    object_schema_cls = LOMUIObjectSchema


__all__ = ("LOMUIJSONSerializer",)
