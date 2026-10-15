# Topic 49: File-by-File Explanation

## In simple words

A useful code reading method connects each file to its caller and security responsibility.

## What this project does

idp_server.py owns identity protocol logic; resource_server.py owns JWKS validation and documents; client_app.py owns redirects, sessions, and API calls; generate_keys.py creates RSA keys; run_all.py starts processes; test_flow.py verifies behavior; templates render user-facing pages.

## Workflow

```text
Entry point -> route -> helper -> external dependency -> output.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
