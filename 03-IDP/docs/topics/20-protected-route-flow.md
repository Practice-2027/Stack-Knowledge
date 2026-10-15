# Topic 20: Protected Route Flow

## In simple words

A protected route rejects requests before business logic runs.

## What this project does

GET /api/profile is decorated with require_token(required_scope='profile'). Once verified, it returns identity data from the token claims. GET and POST /api/data use read and write scopes and query or update SQLite documents.

## Workflow

```text
Request -> middleware -> token claims -> scope -> handler -> response.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
