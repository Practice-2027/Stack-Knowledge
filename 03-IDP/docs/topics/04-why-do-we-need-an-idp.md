# Topic 4: Why Do We Need an IDP?

## In simple words

Without an IDP every application repeats login and password storage.

## What this project does

This project demonstrates one login authority serving a client and a separate API. Centralization enables consistent password handling, token issuance, SSO-style redirects, and shared policy, although a production IDP needs stronger operational controls.

## Workflow

```text
Many app logins -> one IDP -> reusable, audience-specific tokens.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
