# Topic 1: Analyze the Entire Project First

## In simple words

Documentation must follow source code, not assumptions.

## What this project does

The repository contains three Flask services, four HTML templates, two SQLite databases, RSA key files, a runner, and an end-to-end test. The analysis found real OAuth/OIDC, JWT, refresh-token, scope, and session behavior; unimplemented items are called out as recommendations.

## Workflow

```text
Read source -> list routes -> inspect database schema -> trace requests -> separate implemented behavior from production advice.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
