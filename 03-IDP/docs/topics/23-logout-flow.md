# Topic 23: Logout Flow

## In simple words

Logout in this demo clears the client session.

## What this project does

GET /logout calls session.clear() in client_app.py and redirects home. It does not revoke refresh tokens in the IDP or invalidate already-issued JWTs; a still-valid token may work until expiry.

## Workflow

```text
Logout click -> local session cleared -> home; production -> revoke tokens and/or end IDP session.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
