# Topic 11: Login API Documentation

## In simple words

An API contract tells callers exactly what to send and expect.

## What this project does

POST /login accepts username and password as JSON or form data. Success returns access_token, token_type, expires_in, refresh_token, and user profile fields; missing fields return 400 and bad credentials return 401.

## Workflow

```text
POST /login {username,password} -> idp_server.login() -> create_access_token/create_refresh_token -> 200 JSON.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
