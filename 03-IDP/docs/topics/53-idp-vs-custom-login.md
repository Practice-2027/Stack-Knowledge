# Topic 53: IDP vs Custom Login

## In simple words

Custom login is one application feature; an IDP is a reusable trust service.

## What this project does

This repository is a learning implementation of an IDP, not a replacement for hardened products in high-risk production. Dedicated IAM is valuable when many apps, SSO, federation, MFA, lifecycle, compliance, or delegated access are required.

## Workflow

```text
Single app need -> local auth; many apps/security requirements -> shared IDP.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
