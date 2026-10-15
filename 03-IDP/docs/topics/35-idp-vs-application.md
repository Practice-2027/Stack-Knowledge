# Topic 35: IDP vs Application

## In simple words

The IDP proves identity; the application delivers business features.

## What this project does

Here the IDP owns login, users, codes, keys, and tokens. The client owns pages and session handling. The resource server owns document data and business authorization based on scopes.

## Workflow

```text
IDP issues proof -> application presents proof -> resource server serves business data.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
