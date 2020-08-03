from auth.aggregates import User
from auth.gateways import UserGateway
from auth.schemas import external, internal
from common.uow import UnitOfWork


async def resolve_me(_, info):
    raise NotImplementedError


async def resolve_sign_up(_, info, *, email: str, password: str) -> str:
    db = info.context["request"].app.state.db
    redis = info.context["request"].app.state.redis
    async with UnitOfWork(db.transaction(), redis, event_store_schema=internal, event_bus_schema=external) as uow:
        user_aggregate = await uow.aggregate_factory(User, gateway_cls=UserGateway)
        await user_aggregate.sign_up(email, password)
        return user_aggregate.token


async def resolve_user_reference(_, _info, representation):
    raise NotImplementedError
