# Topic 48: Folder Structure

## In simple words

Files are organized by service and responsibility.

## What this project does

Top-level Python files are the three services plus key generation, runner, and tests. templates contains home, login, profile, and data pages. Two SQLite files hold separate domains; PEM files hold signing material.

## Workflow

```text
Service file -> route/helper -> template or database.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
