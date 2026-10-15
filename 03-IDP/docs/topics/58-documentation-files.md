# Topic 58: Documentation Files

## In simple words

Documentation should be modular enough to read one concept at a time.

## What this project does

This deliverable creates docs/topics/01 through 64 as individual Markdown pages, plus a master Markdown document and a complete PDF. The project README is updated with links so the guide is discoverable.

## Workflow

```text
Topic file -> master index -> PDF page -> repository README link.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
