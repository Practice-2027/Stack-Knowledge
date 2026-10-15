# Topic 12: Token Explanation

## In simple words

A token is a portable, time-limited statement issued by a trusted authority.

## What this project does

The IDP creates access tokens; the client stores them in its Flask session; the client sends the access token as Authorization: Bearer to the resource server; the resource server verifies it.

## Workflow

```text
Login -> IDP signs token -> client session -> Bearer header -> API verifies.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
