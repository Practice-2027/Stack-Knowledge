# Topic 64: Accuracy Rules

## In simple words

The documentation must never turn a recommendation into a fact.

## What this project does

This guide is grounded in the inspected files and live SQLite schemas. It explicitly says that roles, password reset, MFA, audit logging, rate limiting, and Kafka are not implemented, and it avoids reproducing secret values or real token strings.

## Workflow

```text
Inspect source -> verify behavior -> document exact file/function -> label gaps -> protect secrets.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
