# Topic 14: JWT Creation Flow

## In simple words

The IDP signs a token only after authentication succeeds.

## What this project does

create_access_token builds claims with a 15-minute lifetime and audience resource_server, then PyJWT signs the token with the RSA private key. create_id_token creates the OIDC identity token for the client audience.

## Workflow

```text
Verified user -> claims -> RS256 private-key signature -> token returned.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
