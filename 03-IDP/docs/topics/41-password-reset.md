# Topic 41: Password Reset

## In simple words

Password reset must prove control of a recovery channel without exposing the old password.

## What this project does

Reset is not implemented. A safe future flow creates a short-lived, single-use, hashed reset token, sends a link, verifies it, updates the password hash, expires sessions/tokens, and records the event.

## Workflow

```text
Forgot password -> generic response -> one-time email link -> new hash -> revoke old auth state.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
