# Topic 33: Database Architecture

## In simple words

The identity database stores identity protocol state; the resource database stores business data.

## What this project does

idp_database.db has users, clients, auth_codes, and refresh_tokens. resource_database.db has user_documents. There are no roles, permissions, sessions, audit_logs, or separate credentials tables.

## Workflow

```text
users -> codes/tokens; token subject -> user_documents.username.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
