# Topic 51: Common Beginner Confusions

## In simple words

Similar-sounding security terms solve different problems.

## What this project does

JWT is a format, not authentication by itself. JWTs are signed rather than encrypted here. OAuth is not JWT; OIDC is not identical to OAuth; an IDP is a service, not merely a database; logout clears this client session but does not revoke JWTs.

## Workflow

```text
Question -> identify protocol/data format/storage -> explain its exact project role.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
