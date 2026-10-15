# Topic 40: MFA

## In simple words

Multi-factor authentication combines different kinds of proof.

## What this project does

MFA is not implemented. A production flow could require password plus authenticator-app OTP, WebAuthn/passkey, or a carefully evaluated notification factor; SMS/email should be treated as weaker recovery channels.

## Workflow

```text
Password -> second factor -> authentication success -> token.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
