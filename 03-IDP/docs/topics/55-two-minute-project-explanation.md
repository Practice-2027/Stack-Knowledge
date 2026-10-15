# Topic 55: Two-Minute Project Explanation

## In simple words

A short explanation should name the trust boundaries and main flow.

## What this project does

Say: this is a Flask IDP ecosystem with a client and resource server. The client redirects to the IDP, receives an authorization code, exchanges it for tokens, stores them in a session, and calls the API with a Bearer JWT. The API verifies RS256 using JWKS and enforces scopes.

## Workflow

```text
Problem -> architecture -> login -> token -> protected API -> security caveat.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
