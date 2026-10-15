# Topic 50: IDP Glossary

## In simple words

A glossary gives beginners a stable vocabulary.

## What this project does

Identity means account information; authentication means proving identity; authorization means permission; access token means API credential; refresh token means token-renewal credential; JWT means signed claims format; OAuth means delegated authorization; OIDC means identity on OAuth; RBAC means role-based access control.

## Workflow

```text
Learn term -> map it to a route/claim/table -> use it in explanations.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
