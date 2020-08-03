import os

from pathlib import Path

from aioredis import create_redis_pool
from ariadne import MutationType, QueryType, gql
from ariadne.asgi import GraphQL
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from asyncpgsa import create_pool
from starlette.applications import Starlette

from auth.resolvers import *

path = (Path(__file__).parent / "schema.graphql").resolve()
type_defs = gql(open(path).read())

query = QueryType()
query.set_field("me", resolve_me)
query.set_field("login", resolve_login)

mutation = MutationType()
mutation.set_field("signUp", resolve_sign_up)

user = FederatedObjectType("User")
user.reference_resolver(resolve_user_reference)

schema = make_federated_schema(type_defs, query, mutation)

application = Starlette(debug=True)
application.mount("/graphql", GraphQL(schema, debug=True))


@application.on_event("startup")
async def setup_app():
    application.state.db = await create_pool(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        database=os.getenv("POSTGRES_DB", "auth"),
        user=os.getenv("POSTGRES_USER", "auth"),
        password=os.getenv("POSTGRES_PASSWORD", "auth"),
        min_size=5,
        max_size=10,
    )
    application.state.redis = await create_redis_pool("redis://%s" % os.getenv("REDIS_HOST", "localhost"))


@application.on_event("shutdown")
async def close_connections():
    await application.state.db.close()
    application.state.redis.close()
