# Topic 34: Database Flow

## In simple words

Database writes and reads are tied to authentication stages.

## What this project does

Registration inserts a hashed user. Login reads the user and creates a refresh-token row. Authorization inserts a one-time code. Token exchange marks that code used and creates tokens. Resource access reads or inserts documents for the token subject.

## Workflow

```text
Validate -> parameterized SQL -> commit -> JSON/HTML result.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
