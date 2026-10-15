# Topic 59: Master Markdown Document

## In simple words

The master guide is the single searchable source of truth.

## What this project does

COMPLETE_IDP_DOCUMENTATION.md combines all 64 topic pages, a project facts summary, endpoint inventory, architecture, workflows, security analysis, glossary, interview guidance, and final flow. It preserves the distinction between implemented features and recommendations.

## Workflow

```text
Repository evidence -> topic pages -> consolidated guide.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
