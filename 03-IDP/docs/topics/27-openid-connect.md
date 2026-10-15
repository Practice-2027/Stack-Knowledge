# Topic 27: OpenID Connect

## In simple words

OIDC adds identity information on top of OAuth 2.0.

## What this project does

The project implements OIDC discovery, an id_token from the code exchange, and /userinfo. OAuth supplies authorization to the resource server; OIDC supplies standardized identity claims to the client.

## Workflow

```text
OIDC discovery -> authorization code -> id_token/access_token -> /userinfo.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
