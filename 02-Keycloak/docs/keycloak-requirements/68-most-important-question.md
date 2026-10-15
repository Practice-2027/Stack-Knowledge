# 68. Most Important Question

> Requirements guide generated from the pasted Keycloak documentation prompt. This page defines what to document; it does not claim that the feature exists in the repository.

## In simple words

Answer exactly what happens after Login is clicked, including where, why, request, response, token, failure, and production equivalent.

## Required workflow

Inspect the repository -> identify the relevant configuration or code -> explain the behavior in plain language -> trace the request/response workflow -> verify every claim against source evidence -> mark missing features explicitly.

## Evidence to capture

- Exact repository file paths and function names.
- Relevant Keycloak realm, client, user, role, scope, mapper, or Docker settings.
- Request and response shape, including status codes and token involvement.
- What is currently implemented.
- What is absent and should be treated only as a production recommendation.

## Safety rules

Use fake examples only. Redact passwords, client secrets, access tokens, refresh tokens, private keys, and sensitive environment values. Never infer a Keycloak feature from documentation alone.

## Expected result

A beginner should be able to explain the concept, follow the workflow, locate the implementation, and distinguish observed behavior from recommended improvements.
