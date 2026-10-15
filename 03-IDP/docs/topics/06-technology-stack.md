# Topic 6: Technology Stack

## In simple words

Each component has a small, clear responsibility.

## What this project does

Python and Flask provide HTTP services; SQLite stores identity and documents; PyJWT creates and reads JWTs; cryptography handles RSA keys; Werkzeug hashes passwords; requests connects services; Flask-CORS allows cross-origin API calls; HTML templates render the UI.

## Workflow

```text
Browser HTTP -> Flask route -> Python logic -> SQLite or service-to-service request.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
