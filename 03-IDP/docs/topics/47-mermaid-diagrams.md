# Topic 47: Mermaid Diagrams

## In simple words

Diagrams make request ownership and trust boundaries visible.

## What this project does

The guide includes text workflows suitable for Mermaid: architecture, registration, login, token creation/validation, protected API, logout, SSO, database relationships, and production architecture. Every diagram should keep the three ports and trust boundaries explicit.

## Workflow

```text
Sequence participants -> request arrows -> validation -> response arrows.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
