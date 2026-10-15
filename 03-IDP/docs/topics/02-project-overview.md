# Topic 2: Project Overview

## In simple words

An IDP centralizes login and issues proof that other services can trust.

## What this project does

The browser starts at the client on port 5005. The client sends the user to the IDP on port 5003; the IDP authenticates the user and issues tokens; the resource server on port 5004 protects profiles and documents.

## Workflow

```text
User -> Client -> IDP login -> authorization code -> client token exchange -> Resource API.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
