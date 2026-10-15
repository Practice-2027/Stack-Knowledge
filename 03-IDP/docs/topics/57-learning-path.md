# Topic 57: Learning Path

## In simple words

Learn the system from transport to production policy.

## What this project does

Level 1 is HTTP/APIs; then authentication; password hashing; JWT and sessions; scopes/RBAC; OAuth; OIDC; SSO; MFA; and production IAM. Each level should be practiced against a route, claim, or test in this repository.

## Workflow

```text
Concept -> small experiment -> observe request/response -> add security reasoning.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
