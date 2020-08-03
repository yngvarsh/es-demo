const { ApolloGateway, RemoteGraphQLDataSource } = require("@apollo/gateway");
const { ApolloServer, AuthenticationError } = require("apollo-server-express");
const express = require("express");
const expressJwt = require("express-jwt");

const port = process.env.APP_PORT | 4000;
const app = express();

app.use(
  expressJwt({
    secret: process.env.AUTH_SECRET,
    algorithms: ["HS256"],
    requestProperty: "decodedJWT",
    credentialsRequired: false
  })
);

app.use(function (err, req, res, next) {
  if (err.name === 'UnauthorizedError') {
    res.status(401).send({"error": `Invalid token: {err.message}`});
  }
});

const gateway = new ApolloGateway({
  serviceList: [{ name: "auth", url: process.env.AUTH_SERVICE_URL }],
  buildService({ name, url }) {
    return new RemoteGraphQLDataSource({
      url,
      willSendRequest({ request, context }) {
        request.http.headers.set("user", context.decodedJWT ? JSON.stringify(context.decodedJWT) : null);
      }
    });
  }
});

const server = new ApolloServer({
  gateway,
  subscriptions: false,
  context: ({ req }) => {
    const decodedJWT = req.decodedJWT || null;
    return { decodedJWT };
  }
});

server.applyMiddleware({ app });

app.listen({ port }, () =>
  console.log(`Server ready at http://localhost:${port}${server.graphqlPath}`)
);
