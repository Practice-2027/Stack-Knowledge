# Topic 39: Production IDP Components

## In simple words

Each production component addresses a failure or security concern.

## What this project does

Useful additions include a load balancer, gateway, identity/token services, Redis for short-lived state, a durable database, audit logging, monitoring, rate limiter, secret manager, KMS/HSM, notifications, and MFA service.

## Workflow

```text
Request -> edge controls -> identity policy -> durable state -> signed result -> audit event.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
