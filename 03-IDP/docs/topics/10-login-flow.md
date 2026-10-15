# Topic 10: Login Flow

## In simple words

Login proves a known user controls the password.

## What this project does

The direct endpoint POST /login looks up username, verifies the stored hash, and returns a short-lived RS256 access token plus a refresh token. The UI normally uses /authorize instead, so the client never receives the user's password.

## Workflow

```text
Credentials -> user lookup -> hash verification -> token creation -> JSON response or 401.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
