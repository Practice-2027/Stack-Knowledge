# Topic 32: Environment Variables

## In simple words

Configuration should be separated from source code.

## What this project does

The resource and client services read IDP_BASE_URL and the client reads RESOURCE_SERVER_URL. The IDP issuer, client ID/secret, redirect URI, lifetimes, and paths are code constants; secrets should move to environment variables or a secret manager.

## Workflow

```text
Environment/config -> service startup -> routes use trusted values.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
