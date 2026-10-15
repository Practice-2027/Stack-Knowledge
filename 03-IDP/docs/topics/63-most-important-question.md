# Topic 63: Most Important Question

## In simple words

A confident answer traces what, why, where, input, output, failure, and production handling.

## What this project does

For this project: username/password enter the IDP authorization form; idp_server.authorize checks the user and stores a code; client_app.callback exchanges it at /token; the client stores tokens in session; resource_server.require_token validates the access token; the endpoint applies a scope and returns the resource.

## Workflow

```text
Input -> route -> helper -> storage/crypto -> output; failures become 400/401/403/409 or redirect messages.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
