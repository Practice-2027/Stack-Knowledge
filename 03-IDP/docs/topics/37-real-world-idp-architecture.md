# Topic 37: Real-World IDP Architecture

## In simple words

Production identity platforms separate edge, identity, keys, sessions, policy, and observability.

## What this project does

This demo compresses those responsibilities into one Flask IDP process and SQLite. A production system commonly adds an API gateway, durable database, key rotation/JWKS publishing, session and token services, audit logs, MFA, and monitoring.

## Workflow

```text
Clients -> gateway -> identity services -> databases/keys/events.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
