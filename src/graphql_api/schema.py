"""GraphQL schema entrypoint."""

import graphene


class Query(graphene.ObjectType):
    """Root GraphQL query placeholder."""

    ping = graphene.String(description="Health check field")

    def resolve_ping(self, info):  # noqa: D401
        return "pong"


class Mutation(graphene.ObjectType):
    """Root GraphQL mutation placeholder."""

    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

