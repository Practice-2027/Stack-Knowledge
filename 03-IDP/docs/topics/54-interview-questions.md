# Topic 54: Interview Questions

## In simple words

Interview preparation is strongest when answers trace this code.

## What this project does

Prepare beginner, intermediate, and advanced questions around routes, password hashing, RS256/JWKS, code replay, scopes, sessions, refresh, OAuth/OIDC, 401 vs 403, key rotation, scaling, and missing controls. The generated topic file contains a compact question bank prompt and project anchors.

## Workflow

```text
Question -> identify exact file/function -> explain tradeoff -> name production improvement.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
