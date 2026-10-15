# Topic 38: Scaling the Simple IDP

## In simple words

Scaling means removing single-process and single-file bottlenecks.

## What this project does

At small scale this local SQLite design is easy to understand. At higher scale use a managed relational database, indexes, multiple stateless service instances, shared session/refresh infrastructure, cache, key rotation, rate limiting, and telemetry.

## Workflow

```text
One process -> replicated services -> shared durable state -> monitored capacity.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
