# Topic 21: Complete API Documentation

## In simple words

The project exposes public, identity, client, and protected-resource endpoints.

## What this project does

IDP: /, /.well-known/openid-configuration, /jwks, /register, /login, /token/refresh, /authorize, /token, /userinfo. Resource: /, /api/health, /api/profile, /api/data GET/POST. Client: /, /login, /callback, /profile, /data GET/POST, /refresh-token, /logout.

## Workflow

```text
Route -> validation/middleware -> database or remote service -> JSON, HTML, redirect, or error.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
