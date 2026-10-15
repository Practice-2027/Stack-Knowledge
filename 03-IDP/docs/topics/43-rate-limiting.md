# Topic 43: Rate Limiting

## In simple words

Authentication endpoints are attractive targets for brute-force attacks.

## What this project does

No rate limiter or account lockout is implemented. Production should throttle by account and network signals, add monitoring and progressive delays, and consider CAPTCHA only where appropriate.

## Workflow

```text
Repeated attempts -> limiter -> delay/block/challenge -> alert.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
