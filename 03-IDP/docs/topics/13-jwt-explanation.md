# Topic 13: JWT Explanation

## In simple words

JWT is a signed data format: HEADER.PAYLOAD.SIGNATURE.

## What this project does

This project uses RS256 and key id idp-key-1. Access-token claims include iss, sub, aud, iat, exp, user_id, email, name, and scope. JWT payloads are readable; the signature protects integrity but does not encrypt the contents.

## Workflow

```text
Header names algorithm/key -> payload carries claims -> signature proves IDP signed the exact bytes.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
