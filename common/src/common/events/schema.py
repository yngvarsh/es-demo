import ujson

from marshmallow import Schema, fields
from marshmallow_dataclass import class_schema
from marshmallow_oneofschema import OneOfSchema


class EventMetaSchema(Schema):
    aggregate_id = fields.UUID(required=True)
    aggregate_version = fields.Integer(required=True)
    created_at = fields.DateTime(required=True)

    class Meta:
        render_module = ujson


class BaseSchema(Schema):
    meta = fields.Nested(EventMetaSchema)

    class Meta:
        render_module = ujson


class EventSchema(OneOfSchema):
    type_field = "event_type"
    type_schemas = {}

    @classmethod
    def register(cls, event_cls, *, schema=None):
        if schema is None:
            schema = class_schema(event_cls, base_schema=BaseSchema)
        cls.type_schemas.setdefault(event_cls.__name__, schema)
        return event_cls
