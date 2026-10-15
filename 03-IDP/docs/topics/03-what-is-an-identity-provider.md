# Topic 3: What Is an Identity Provider?

## In simple words

An IDP answers: who is this person?

## What this project does

Identity is the user record; authentication proves the user; authorization decides what the user may do. In the building analogy, the IDP is the security gate, the token is an entry pass, and the resource API is a restricted room.

## Workflow

```text
Credentials -> identity check -> signed pass -> API checks pass and permission.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
