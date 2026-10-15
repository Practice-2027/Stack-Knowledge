# Topic 7: Complete User Authentication Flow

## In simple words

Login is a chain of verifiable steps, not one magic action.

## What this project does

The normal UI path is OAuth Authorization Code: the client creates state, the IDP checks credentials, the IDP stores a one-time code, the client exchanges it, and the API later verifies the access token.

## Workflow

```text
Login click -> state -> /authorize -> password check -> code -> /token -> access/id/refresh tokens -> API call.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
