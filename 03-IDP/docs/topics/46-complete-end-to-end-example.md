# Topic 46: Complete End-to-End Example

## In simple words

The most important story is login followed by a protected API request.

## What this project does

The browser uses client_app.login, the IDP's authorize route verifies credentials and creates a code, client_app.callback calls /token, and client_app.profile calls resource /api/profile. The resource middleware validates the token and scope before returning the profile.

## Workflow

```text
Click login -> /authorize -> code -> /callback -> /token -> session -> /api/profile -> 200.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
