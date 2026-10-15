# Topic 44: Debugging Guide

## In simple words

Debug from the outside inward, following one request at a time.

## What this project does

For login, check redirect URL, state, form fields, IDP logs, user row, password verifier, and token response. For 401, check the Bearer header, kid/alg, JWKS, issuer, audience, expiry, and refresh path. For 403, inspect the required scope.

## Workflow

```text
Browser -> client log -> IDP log -> resource log -> response status.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
