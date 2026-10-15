# Topic 52: Kafka / Microservices Integration

## In simple words

Events can notify other services without coupling them to login requests.

## What this project does

Kafka is not present. A future user-created event could feed notification, analytics, or provisioning services, but identity creation should succeed or fail independently from noncritical consumers.

## Workflow

```text
Registration -> committed user -> event -> consumers -> retries/dead-letter handling.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
