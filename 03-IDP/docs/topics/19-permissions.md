# Topic 19: Permissions

## In simple words

Permissions are the small actions an API allows.

## What this project does

The implemented permission-like values are OAuth scopes: openid, profile, email, read, and write. resource_server.py checks profile on /api/profile, read on GET /api/data, and write on POST /api/data.

## Workflow

```text
Scope claim -> required_scope -> 200 or 403 insufficient_scope.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
