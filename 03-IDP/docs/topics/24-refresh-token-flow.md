# Topic 24: Refresh Token Flow

## In simple words

Refresh tokens let the client obtain a new access token without asking for the password again.

## What this project does

The IDP stores opaque refresh tokens in SQLite with username, client_id, scope, expiry, and revoked flag. The client retries a 401 once by posting grant_type=refresh_token to /token; access tokens last 15 minutes and refresh tokens seven days.

## Workflow

```text
Expired access token -> refresh token -> IDP lookup/expiry/revocation check -> new access token -> retry.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
