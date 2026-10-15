# Topic 9: Password Security

## In simple words

The database stores a password hash, never the original password.

## What this project does

idp_server.py uses generate_password_hash during registration and check_password_hash during login. The algorithm is delegated to Werkzeug; the code never needs to reverse the hash.

## Workflow

```text
Password -> salted one-way hash -> database; entered password -> verifier -> match or reject.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
