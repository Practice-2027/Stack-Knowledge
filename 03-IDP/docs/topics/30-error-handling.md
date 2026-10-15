# Topic 30: Error Handling

## In simple words

Errors tell the caller whether to fix input, authenticate, or change permissions.

## What this project does

The code uses 400 for malformed requests, 401 for missing/invalid credentials or tokens, 403 for missing scopes, 404 for missing users, 409 for duplicate registration, and 201/200 for successful writes/reads. Database and network failures are logged but not consistently mapped to a production error model.

## Workflow

```text
Failure -> status code + JSON/HTML message -> client redirect, retry, or display.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
