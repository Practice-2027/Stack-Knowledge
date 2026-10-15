# Topic 16: Cookies vs Local Storage vs Memory

## In simple words

Where authentication state is stored changes the attack surface.

## What this project does

This client uses Flask's session cookie mechanism to hold access_token, refresh_token, id_token, and user data. The code does not use localStorage or sessionStorage. The current app generates a random SECRET_KEY at startup, so sessions are invalidated on restart; production should use a stable secret and secure cookie flags.

## Workflow

```text
OAuth callback -> server session values -> browser cookie -> client reads session on later requests.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
