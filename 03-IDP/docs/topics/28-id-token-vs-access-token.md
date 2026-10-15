# Topic 28: ID Token vs Access Token

## In simple words

These tokens have different audiences and jobs.

## What this project does

The id_token is created for client_app_demo and describes the authenticated user. The access token is created for audience resource_server and is sent to protected APIs. The API must not use an ID token as an API credential.

## Workflow

```text
ID token -> client identity; access token -> resource API authorization.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
