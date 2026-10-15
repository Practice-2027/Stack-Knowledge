# Topic 8: User Registration Flow

## In simple words

Registration creates an identity record after basic validation.

## What this project does

POST /register accepts JSON or form data with username, email, password, and optional full_name. It rejects missing fields, passwords under six characters, and duplicate username/email values, then stores a salted Werkzeug hash.

## Workflow

```text
Form -> POST /register -> validate -> duplicate check -> hash -> INSERT users -> 201 response.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
