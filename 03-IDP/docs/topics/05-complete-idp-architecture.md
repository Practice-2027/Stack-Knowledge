# Topic 5: Complete IDP Architecture

## In simple words

The architecture separates identity, user experience, and business data.

## What this project does

The IDP owns users and token signing. The client owns browser pages and its Flask session. The resource server owns private documents and verifies tokens with the IDP public key rather than receiving the private key.

## Workflow

```text
Browser -> client:5005 -> IDP:5003; client -> resource:5004; resource -> IDP JWKS when its key cache expires.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
