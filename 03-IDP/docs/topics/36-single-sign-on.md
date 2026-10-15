# Topic 36: Single Sign-On

## In simple words

SSO means one IDP login can serve multiple client applications.

## What this project does

The current demo has one registered client, but its authorization-code design is the foundation for SSO. Additional clients would need registered IDs, validated redirect URIs, and an IDP browser session to avoid repeated login.

## Workflow

```text
App A -> IDP session -> App B/App C receive their own audience-specific tokens.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
