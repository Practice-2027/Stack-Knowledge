# Topic 45: Testing

## In simple words

Tests turn an authentication flow into repeatable evidence.

## What this project does

test_flow.py exercises discovery, JWKS, registration, direct login, refresh, authorization code, replay prevention, UserInfo, protected profile/data, missing token, and tampered-token rejection. Password reset, MFA, role policy, and logout revocation tests are absent because those features are absent.

## Workflow

```text
Start services -> run test_flow.py -> assert status, claims, and security behavior.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
