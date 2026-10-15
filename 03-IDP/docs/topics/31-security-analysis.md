# Topic 31: Security Analysis

## In simple words

The project demonstrates important controls but is educational, not production-ready.

## What this project does

Implemented: password hashing, RS256 signatures, issuer/audience/expiry checks, state checking, one-time authorization codes, refresh expiry/revocation fields, parameterized SQLite queries, and scopes. Gaps: HTTP URLs, permissive CORS, hard-coded client secret, key files in the repo, no rate limiting, no MFA, no audit log, and no strict redirect validation at the token endpoint.

## Workflow

```text
Control -> threat reduced; missing control -> production work item.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
