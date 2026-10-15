# Topic 22: Authentication API Categories

## In simple words

Grouping endpoints makes a large API easier to learn.

## What this project does

Registration is /register; direct login is /login; OAuth login is /authorize plus /token; refresh is /token/refresh or /token with grant_type refresh_token; identity is /userinfo; protected resources are /api/profile and /api/data. Password reset, role management, and permission management are not implemented.

## Workflow

```text
Choose category -> call endpoint -> receive identity/token/resource result.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
