# Topic 61: PDF Quality Check

## In simple words

A document is not complete until its rendering is inspected.

## What this project does

The generated PDF uses fixed margins, page breaks, readable fonts, page numbers, and compact tables. Validation checks page count, extracted topic headings, presence of page numbering, and rendered page images for clipping or overlap.

## Workflow

```text
Generate -> render PNGs -> inspect representative pages -> extract text -> final check.
```

## Project anchor

This repository is a three-service Flask demonstration: idp_server.py (IDP, port 5003), resource_server.py (protected API, port 5004), and client_app.py (web client, port 5005).

## Implemented vs production

Implemented here: SQLite users/clients/authorization codes/refresh tokens, Werkzeug password hashing, OAuth 2.0 Authorization Code flow, OIDC discovery and UserInfo, RS256 JWTs, JWKS verification, scopes, refresh, client sessions, and protected documents.

Production improvement: move secrets and keys to a secret manager, use HTTPS, tighten cookie settings and CORS, validate redirect URIs strictly, add rate limiting and audit logs, and use a mature IAM product or hardened service design.
