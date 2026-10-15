# Topic 56: Five-Minute Technical Explanation

## In simple words

A deeper explanation adds claims, databases, errors, and tradeoffs.

## What this project does

Walk through browser, client state, IDP users and codes, RSA signing, token lifetimes, callback exchange, JWKS cache, issuer/audience checks, scope enforcement, SQLite documents, refresh, logout, and production gaps.

## Workflow

```text
User -> client -> IDP -> authN -> code/tokens -> API authN -> authZ -> resource.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
