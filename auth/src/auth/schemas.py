from secrets import token_hex

from marshmallow import post_dump

from common.events.impl import UserSignedUp
from common.events.schema import BaseSchema, EventSchema


class BaseUserSignedUpSchema(BaseSchema):
    @post_dump
    def obfuscate_password(self, obj, *args, **kwargs):
        if not self.context["internal"]:
            obj["password"] = token_hex(60)
        return obj


EventSchema.register(UserSignedUp, custom_base=BaseUserSignedUpSchema)

internal = EventSchema(context={"internal": True})
external = EventSchema(context={"internal": False})
