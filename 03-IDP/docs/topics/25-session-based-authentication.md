# Topic 25: Session-Based Authentication

## In simple words

A session links a browser to server-side application state.

## What this project does

The client uses Flask sessions to remember OAuth tokens and profile data between requests. The IDP and resource server do not use login sessions for API authorization; they use tokens.

## Workflow

```text
Browser cookie -> client Flask session -> token added to outbound API request.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
