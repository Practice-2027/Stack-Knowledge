# Custom Identity Provider (IDP) from Scratch

## Complete generated documentation

The repository now includes a beginner-friendly implementation guide based on the actual source code:

- [Complete IDP Documentation (Markdown)](docs/COMPLETE_IDP_DOCUMENTATION.md)
- [Complete IDP Documentation (PDF)](docs/COMPLETE_IDP_DOCUMENTATION.pdf)
- [IDP Workflow Deep Dive with Diagrams (PDF)](docs/IDP_WORKFLOW_DEEP_DIVE.pdf)
- [Individual topic pages](docs/topics/)

The supplied documentation prompt contains 64 numbered requirements (1-64), so the generated guide preserves all 64 topics. It explicitly separates implemented features from production recommendations.

A complete, beginner-friendly educational Identity Provider (IDP) and federated authorization system built in pure Python.

This project demystifies how modern Single Sign-On (SSO) systems work internally—such as **Auth0**, **Keycloak**, **Okta**, and **Google Identity**—by implementing the core mechanics from scratch without heavy frameworks or cloud vendor dependencies.

---

## Table of Contents
1. [What is an Identity Provider (IDP)?](#what-is-an-identity-provider-idp)
2. [IDP vs Authentication vs Authorization](#idp-vs-authentication-vs-authorization)
3. [Key Concepts Explained](#key-concepts-explained)
4. [How JWT Tokens Work (Deep Dive)](#how-jwt-tokens-work-deep-dive)
5. [Three-Server Architecture](#three-server-architecture)
6. [OAuth 2.0 Authorization Code Flow Diagram](#oauth-20-authorization-code-flow-diagram)
7. [Project File Structure](#project-file-structure)
8. [Prerequisites](#prerequisites)
9. [Step-by-Step Setup (Windows)](#step-by-step-setup-windows)
10. [How to Run and Test](#how-to-run-and-test)
11. [Step-by-Step Flow Walkthrough](#step-by-step-flow-walkthrough)
12. [Token Inspection Guide](#token-inspection-guide)
13. [Common Errors & Troubleshooting](#common-errors--troubleshooting)
14. [Comparison: Custom IDP vs Keycloak vs Auth0](#comparison-custom-idp-vs-keycloak-vs-auth0)
15. [Learning Exercises](#learning-exercises)

---

## What is an Identity Provider (IDP)?

In traditional web applications, every website maintained its own user database with usernames and passwords. If you used 20 different websites, you had 20 different accounts.

An **Identity Provider (IDP)** is a centralized service that:
1. Stores and manages digital identities (user accounts, passwords, MFA).
2. Verifies who a user is (Authentication).
3. Issues digitally signed security credentials (Tokens) to other applications on behalf of the user.

### Real-World Analogy: The Passport Office
Think of an Identity Provider like a **Government Passport Agency**:
* **You (The User)** apply for a passport by proving your identity (entering your credentials).
* **The Passport Agency (IDP)** verifies your identity and issues you a **tamper-evident Passport (JWT Access Token)** stamped with an official holographic seal (Cryptographic Signature).
* When you travel to **Border Control / Airports (Resource Server API)**, the officer does not call your parents or check your birth certificate; they simply verify the **authenticity of the official seal** on your passport.
* The border officer does not need access to the government's private stamping press—they only need the official public stamping verification rules (**JWKS**).

---

## IDP vs Authentication vs Authorization

Beginners often confuse these three fundamental security concepts:

| Concept | Question It Answers | Example in This Project |
| :--- | :--- | :--- |
| **Identity Provider (IDP)** | *Where is your identity managed?* | The server on port `5003` that holds user accounts and issues tokens. |
| **Authentication (AuthN)** | *Who are you? Are you really who you say you are?* | Entering your password on the IDP login screen to prove you are Alice. |
| **Authorization (AuthZ)** | *What actions are you allowed to perform?* | Checking if your token contains the `read` or `write` scope to access `/api/data`. |

```
+--------------------------------------------------------------------------+
| AUTHENTICATION (AuthN)                 AUTHORIZATION (AuthZ)             |
| "Are you Alice?"                       "Can Alice edit document #42?"    |
| Verified once by IDP                   Verified on every API call by     |
| using password / biometrics            Resource Server using Token Scopes|
+--------------------------------------------------------------------------+
```

---

## Key Concepts Explained

### 1. JSON Web Token (JWT)
A compact, URL-safe means of representing claims to be transferred between two parties. JWTs are stateless: all user claims are embedded in the token itself, so the API server does not need to query a central database for every request.

### 2. OAuth 2.0
An **authorization framework** that allows a third-party application to obtain limited access to an HTTP service on behalf of a resource owner without exposing the user's password to the client app.

### 3. OpenID Connect (OIDC)
A thin **identity layer** built on top of OAuth 2.0. While OAuth 2.0 is designed for *delegation* (giving permissions), OIDC standardizes *identity* (who is the logged-in user) by introducing the `id_token` and the `/userinfo` endpoint.

### 4. Authorization Code Flow
The most secure OAuth 2.0 grant type for server-side applications. It divides the authorization into two stages:
* **Front-Channel (Browser)**: The user logs in at the IDP and is redirected back with a short-lived, single-use `authorization_code`.
* **Back-Channel (Server-to-Server)**: The client application exchanges this code for access and refresh tokens directly over a secure HTTP POST request. The user's browser never sees the access token in URL parameters.

### 5. Access Token vs. Refresh Token
* **Access Token**: Short-lived (e.g., 15 minutes). Sent in the `Authorization: Bearer <token>` header on every API request. If intercepted, the attacker's window of opportunity is minimal.
* **Refresh Token**: Long-lived (e.g., 7 days). Kept secret on the client server. Used exclusively to obtain fresh access tokens from the IDP without prompting the user to re-type their password.

### 6. JSON Web Key Set (JWKS)
A set of public cryptographic keys published by the IDP at `http://localhost:5003/jwks`. Resource servers fetch this set to verify the signatures of incoming JWTs. Because the keys are asymmetric (RSA), the Resource Server only needs the **Public Key** and never has access to the **Private Key**.

---

## How JWT Tokens Work (Deep Dive)

A JWT is a single string made of **three distinct parts separated by dots (`.`)**:

$$\text{JWT} = \underbrace{\text{Header}}_{\text{Red}} \;.\; \underbrace{\text{Payload}}_{\text{Purple}} \;.\; \underbrace{\text{Signature}}_{\text{Cyan}}$$

```
eyJhbGciOiJSUzI1NiIsImtpZCI6ImlkcC1rZXktMSJ9.
eyJzdWIiOiJhbGljZSIsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3Q6NTAwMyIsImV4cCI6MTc5MTkxODAwMH0.
dBj4P_1e002pU_v_14mP42jO7_e_7Qk81jBqL...
```

### 1. Header (Algorithm & Key Metadata)
The header is Base64URL-encoded JSON declaring the signing algorithm and the key identifier (`kid`):
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "idp-key-1"
}
```
* `alg`: Algorithm used (`RS256` = RSA Signature with SHA-256).
* `kid`: Key ID indicating which public key in the JWKS corresponds to this token.

### 2. Payload (Claims)
The payload contains the **claims**—statements about the user and token metadata:
```json
{
  "iss": "http://localhost:5003",
  "sub": "alice",
  "aud": "resource_server",
  "iat": 1791917100,
  "exp": 1791918000,
  "email": "alice@example.com",
  "name": "Alice Smith",
  "scope": "openid profile email read write"
}
```
* `iss` (Issuer): URL of the IDP that minted the token.
* `sub` (Subject): Unique identifier of the authenticated user.
* `aud` (Audience): Who the token is intended for (`resource_server`).
* `exp` (Expiration): Unix timestamp when the token becomes invalid.
* `iat` (Issued At): Unix timestamp when the token was created.
* `scope`: Space-delimited permissions granted to this token.

### 3. Signature (Cryptographic Verification)
The signature guarantees that the token has **not been altered or forged**:
$$\text{Signature} = \text{RSA-SHA256}\Big(\text{Base64URL}(\text{Header}) + \text{"."} + \text{Base64URL}(\text{Payload}), \; \text{IDP Private Key}\Big)$$

Anyone can decode and view the Header and Payload (JWTs are **signed, not encrypted**), but **nobody can alter even a single byte** without invalidating the mathematical signature verified by the IDP's public key.

---

## Three-Server Architecture

This project splits responsibilities cleanly across three separate HTTP services:

```
+-----------------------------------------------------------------------------------------+
|                                    USER BROWSER                                         |
+-----------------------------------------------------------------------------------------+
       |                                      ^                                 |
       | 1. Visit App                         | 3. Redirect to IDP Form         | 5. Redirect back
       v                                      |                                 v    with auth code
+-----------------------+              +-----------------------+        +-----------------------+
|  CLIENT APPLICATION   |              |   IDENTITY PROVIDER   |        |  PROTECTED RESOURCE   |
|     (Port 5005)       |              |      (Port 5003)      |        |     SERVER (API)      |
|                       |              |                       |        |     (Port 5004)       |
| * Web frontend        |              | * SQLite User Store   |        | * SQLite Private Data |
| * Session token store |              | * RSA Private Key     |        | * NO private keys!    |
| * Initiates OAuth     |              | * Issues JWTs & codes |        | * Validates tokens via|
| * Calls Resource API  |              | * Publishes /jwks     |        |   IDP's /jwks endpoint|
+-----------------------+              +-----------------------+        +-----------------------+
       |                                      ^        ^                            ^
       | 4. POST /token (Exchange Code)       |        |                            |
       +--------------------------------------+        | 6. Fetch JWKS Public Keys  |
       |                                               +----------------------------+
       | 7. GET /api/data (Authorization: Bearer <JWT>)                             |
       +----------------------------------------------------------------------------+
```

| Server Name | Port | Description |
| :--- | :--- | :--- |
| **`idp_server.py`** | `5003` | The central Identity Provider. Manages users, credentials, RSA keys, auth codes, and token signing. |
| **`resource_server.py`** | `5004` | The Protected API. Hosts confidential user documents and validates tokens using JWKS without a shared secret. |
| **`client_app.py`** | `5005` | The Client Web App. Consumes identity from the IDP and calls the Resource Server with access tokens. |

---

## OAuth 2.0 Authorization Code Flow Diagram

Here is the exact step-by-step communication sequence executed when you log in:

```
User (Browser)           Client App (:5005)           IDP Server (:5003)        Resource Server (:5004)
     |                          |                            |                             |
     |--- 1. Click Login ------>|                            |                             |
     |                          |-- 2. Redirect to IDP ----->|                             |
     |<-- 3. Show Login Page ---+                            |                             |
     |                                                       |                             |
     |--- 4. Enter Alice / password123 --------------------->|                             |
     |                                                       |-- Verify credentials        |
     |                                                       |-- Generate auth_code        |
     |<-- 5. Redirect to :5005/callback?code=AUTH_CODE ------|                             |
     |                                                       |                             |
     |--- 6. GET /callback?code=AUTH_CODE ------------------>|                             |
     |                          |                            |                             |
     |                          |-- 7. POST /token --------->|                             |
     |                          |      (code, client_id)     |-- Validate code & expiry    |
     |                          |                            |-- Sign RS256 JWT Access Tok |
     |                          |<-- 8. Return Tokens -------|                             |
     |                          |       (access_token,       |                             |
     |                          |        refresh_token)      |                             |
     |                          |                            |                             |
     |                          |-- 9. Save tokens in session|                             |
     |<-- 10. Redirect /profile |                            |                             |
     |                          |                            |                             |
     |--- 11. GET /data ------->|                            |                             |
     |                          |-- 12. GET /api/data ------------------------------------>|
     |                          |       Header: Bearer <JWT> |                             |
     |                          |                            |<-- 13. GET /jwks (Cached) --|
     |                          |                            |    (Retrieve Public Key)    |
     |                          |                            |                             |
     |                          |                            |    [Verify RS256 Signature] |
     |                          |                            |    [Verify Expiration Time] |
     |                          |                            |    [Verify 'read' Scope]    |
     |                          |<-- 14. 200 OK + Data ------------------------------------|
     |<-- 15. Render Data Page -|                            |                             |
```

---

## Project File Structure

```
c:\Users\itzme\Desktop\All Stacks\03-IDP\
│
├── requirements.txt           # Python dependencies (flask, PyJWT, cryptography, etc.)
├── generate_keys.py           # RSA 2048-bit key pair generator
├── idp_server.py              # Identity Provider server (Port 5003)
├── resource_server.py         # Protected API server (Port 5004)
├── client_app.py              # Client web application (Port 5005)
├── run_all.py                 # Master runner starting all 3 servers simultaneously
├── test_flow.py               # Automated end-to-end test suite (10 automated checks)
│
├── templates/                 # Clean, responsive HTML templates (100% inline CSS)
│   ├── login_form.html        # IDP Single Sign-On & Consent UI (Port 5003)
│   ├── home.html              # Client App Landing Page (Port 5005)
│   ├── profile.html           # User Profile & Interactive JWT Inspector (Port 5005)
│   └── data.html              # Protected Documents Management Page (Port 5005)
│
├── private_key.pem            # RSA Private Key (Created by generate_keys.py)
├── public_key.pem             # RSA Public Key (Created by generate_keys.py)
├── idp_database.db            # SQLite DB for IDP users, codes & refresh tokens
└── resource_database.db       # SQLite DB for Resource Server documents
```

---

## Prerequisites

* **Operating System**: Windows 10/11, macOS, or Linux.
* **Python**: Python 3.8 or newer (tested and verified on Python 3.13).
* **Network**: Ports `5003`, `5004`, and `5005` free on your machine.
* **No Docker required**: 100% pure Python using SQLite.

---

## Step-by-Step Setup (Windows)

Open **PowerShell** or **Command Prompt** and navigate to the project directory:

```powershell
cd "c:\Users\itzme\Desktop\All Stacks\03-IDP"
```

### 1. (Optional) Create and Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If on Command Prompt: `.\venv\Scripts\activate.bat`)*

### 2. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Generate RSA Key Pair
Run the key generator script to create the RSA 2048-bit public and private keys:
```powershell
python generate_keys.py
```
Output:
```
[KEYS] Generating new 2048-bit RSA key pair...
[KEYS] Key pair generated successfully!
[KEYS] -> Private key saved to: ...\private_key.pem
[KEYS] -> Public key saved to:  ...\public_key.pem
```

---

## How to Run and Test

### Method A: Start All 3 Servers at Once (Recommended)

Run the master orchestrator script:
```powershell
python run_all.py
```

You will see a live dashboard in your terminal streaming prefixed logs from all three servers:
```
========================================================================
   CUSTOM IDENTITY PROVIDER (IDP) & OAUTH 2.0 / OIDC ECOSYSTEM
========================================================================
  All 3 servers are starting up in parallel:

  1. Identity Provider (IDP):
     * Home:           http://localhost:5003
     * JWKS Keys:      http://localhost:5003/jwks
     * OIDC Discovery: http://localhost:5003/.well-known/openid-configuration

  2. Protected Resource Server:
     * Base API:       http://localhost:5004
     * Profile:        http://localhost:5004/api/profile
     * Protected Data: http://localhost:5004/api/data

  3. Client Web Application (START HERE!):
     * Web Portal:     http://localhost:5005

  Pre-configured Demo Test Accounts:
     * Username: alice   | Password: password123
     * Username: bob     | Password: secret456
========================================================================
```

Open your browser and navigate to:
👉 **[http://localhost:5005](http://localhost:5005)**

---

### Method B: Start Each Server Manually (In Separate Terminals)

If you prefer to inspect each server in its own PowerShell terminal window:

**Terminal 1 — Identity Provider:**
```powershell
python idp_server.py
```

**Terminal 2 — Resource Server:**
```powershell
python resource_server.py
```

**Terminal 3 — Client Application:**
```powershell
python client_app.py
```

---

### Method C: Run the Automated Verification Suite

With the servers running, open another terminal window and run:
```powershell
python test_flow.py
```

This automated test suite runs 10 end-to-end checks:
1. `[PASS]` IDP OIDC Discovery (`/.well-known/openid-configuration`)
2. `[PASS]` IDP JWKS Public Key Set (`/jwks`)
3. `[PASS]` User Registration (`POST /register`)
4. `[PASS]` Direct Login (`POST /login`)
5. `[PASS]` Dedicated Refresh Token Endpoint (`POST /token/refresh`)
6. `[PASS]` OAuth 2.0 Authorization Code Flow (`/authorize` -> `/token`)
7. `[PASS]` Single-Use Authorization Code Replay Attack Prevention
8. `[PASS]` OIDC UserInfo Endpoint (`GET /userinfo`)
9. `[PASS]` Resource Server Profile Verification via JWKS (`GET /api/profile`)
10. `[PASS]` Resource Server Protected Data List & Creation (`GET/POST /api/data`)
11. `[PASS]` Security: Cryptographically Tampered Token Rejection (`401 Unauthorized`)

---

## Step-by-Step Flow Walkthrough

Here is what happens under the hood as you interact with the UI:

### Step 1: Visit Client Application
1. Navigate to `http://localhost:5005`.
2. The client checks its session cookie. Because you are not logged in, it shows the login button.
3. Click **"Sign In with Custom IDP (Port 5003)"**.

### Step 2: The OAuth 2.0 Redirect
1. The client app generates a random, cryptographically secure `state` parameter and stores it in your session.
2. The browser is redirected to:
   ```
   http://localhost:5003/authorize?response_type=code&client_id=client_app_demo&redirect_uri=http://localhost:5005/callback&scope=openid+profile+email+read+write&state=xyz123
   ```
3. The IDP validates that `client_app_demo` is registered and renders the SSO consent page (`login_form.html`).

### Step 3: Authenticate at the IDP
1. Use either the pre-seeded credentials or register a new user:
   * **Alice**: `alice` / `password123`
   * **Bob**: `bob` / `secret456`
2. Click **"Sign In & Grant Access"**.
3. The IDP validates the password using Werkzeug's salted SHA-256 hash check.
4. The IDP generates a secure, one-time `authorization_code` (e.g. `Zlc-GmpeDsQ4RXs5...`), saves it to SQLite with a 5-minute expiration, and issues a 302 redirect:
   ```
   http://localhost:5005/callback?code=Zlc-GmpeDsQ4RXs5...&state=xyz123
   ```

### Step 4: Token Exchange (Back-Channel)
1. Your browser lands on `http://localhost:5005/callback`.
2. The client app verifies that `state` matches the value saved in session (CSRF protection).
3. The client app executes an internal HTTP POST request directly to the IDP:
   ```http
   POST http://localhost:5003/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code&code=Zlc-GmpeDsQ4RXs5...&client_id=client_app_demo&client_secret=super-secret-client-password
   ```
4. The IDP verifies the code, **marks it as used immediately** (preventing replay attacks), and signs two tokens using its RSA Private Key:
   * `access_token` (JWT with 15-minute lifespan)
   * `refresh_token` (Opaque 48-byte token with 7-day lifespan)
5. The client app saves both tokens inside the secure server session and redirects to `/profile`.

### Step 5: Accessing the Protected Resource Server
1. The client app calls `http://localhost:5004/api/profile` with header:
   ```http
   Authorization: Bearer <access_token>
   ```
2. The Resource Server reads the `kid` from the token header (`idp-key-1`), fetches the public key from `http://localhost:5003/jwks`, and verifies:
   * Signature is mathematically valid.
   * `exp` timestamp is still in the future.
   * `iss` matches `http://localhost:5003`.
   * `aud` matches `resource_server`.
3. The Resource Server returns the profile data!

---

## Token Inspection Guide

When you visit **Profile & JWT Inspector** (`http://localhost:5005/profile`), the application splits the raw JWT into its three parts:

```
[Raw Header (Red)] . [Raw Payload (Purple)] . [Raw Signature (Cyan)]
```

### Inspecting Manually with Python
You can inspect any token from the command line:

```python
import jwt
import json

token = "YOUR_ACCESS_TOKEN_HERE"

# 1. Inspect Header without verification
header = jwt.get_unverified_header(token)
print("HEADER:", json.dumps(header, indent=2))

# 2. Inspect Claims without verification
claims = jwt.decode(token, options={"verify_signature": False})
print("PAYLOAD:", json.dumps(claims, indent=2))
```

### Verifying with the Public Key
```python
import jwt

with open("public_key.pem", "rb") as f:
    public_key = f.read()

# Validates mathematical signature, issuer, and expiration
decoded = jwt.decode(
    token,
    public_key,
    algorithms=["RS256"],
    issuer="http://localhost:5003",
    audience="resource_server"
)
print("Signature is VALID! Authenticated user:", decoded["sub"])
```

---

## Common Errors & Troubleshooting

### 1. `Address already in use` or Port Conflicts
* **Symptom**: `OSError: [Errno 98] Address already in use` or Windows socket error `10048`.
* **Cause**: Another service or previous run is already listening on port 5003, 5004, or 5005.
* **Fix (PowerShell)**:
  ```powershell
  Get-NetTCPConnection -LocalPort 5003,5004,5005 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  ```

### 2. `Invalid token: Signature verification failed`
* **Symptom**: Resource server returns HTTP 401 when verifying tokens.
* **Cause**: The RSA keys were regenerated while the server had an old key cached, or the token was signed with a different private key.
* **Fix**: Delete `private_key.pem` and `public_key.pem`, re-run `python generate_keys.py`, and restart `python run_all.py`.

### 3. `Token has expired` (HTTP 401)
* **Symptom**: After 15 minutes of inactivity, API calls return `401 Unauthorized`.
* **Fix**: Click the **"↻ Refresh Token"** button in the navigation bar. The client app uses the long-lived refresh token to obtain a fresh 15-minute access token automatically without re-entering credentials!

### 4. `State parameter mismatch (CSRF suspected)`
* **Symptom**: Callback returns an error after clicking login.
* **Cause**: Session cookie was cleared, or browser opened multiple simultaneous login tabs.
* **Fix**: Return to `http://localhost:5005` and click login again.

---

## Comparison: Custom IDP vs Keycloak vs Auth0

| Feature | This Custom IDP | Keycloak | Auth0 / Okta |
| :--- | :--- | :--- | :--- |
| **Primary Purpose** | Educational & transparency | Self-hosted enterprise SSO | Managed SaaS cloud identity |
| **Language / Tech** | Python (Flask + PyJWT) | Java (WildFly / Quarkus) | Proprietary Cloud Platform |
| **Setup Complexity** | Zero setup (single command) | Medium-High (Docker / DB) | Low (Cloud signup) |
| **Token Verification** | RS256 via `/jwks` | RS256 / ES256 via `/jwks` | RS256 via `/jwks` |
| **Code Inspection** | 100% visible code (~200 lines) | Complex Java codebase | Closed source |
| **MFA / Social Logins** | Optional exercise | Built-in out of the box | Built-in out of the box |
| **User Directory** | SQLite | PostgreSQL / MySQL / LDAP | Cloud Multi-tenant DB |
| **Resource Overhead** | < 50 MB RAM total | ~500 MB – 1.5 GB RAM | 0 local resources |

---

## Learning Exercises

Now that you understand the core mechanics, try extending the system with these hands-on challenges:

1. **Add Proof Key for Code Exchange (PKCE)**:
   * Generate a random `code_verifier` on the client.
   * Send `code_challenge = SHA256(code_verifier)` to `/authorize`.
   * Verify the challenge at `/token` to protect public clients against code interception.

2. **Add Multi-Factor Authentication (MFA / TOTP)**:
   * Integrate Python's `pyotp` library.
   * Require a 6-digit authenticator code on `/authorize` before generating the authorization code.

3. **Implement Token Revocation (Blacklist)**:
   * Add a `POST /token/revoke` endpoint to invalidate refresh tokens early when a user logs out.

4. **Add Role-Based Access Control (RBAC)**:
   * Add a `role` column to the `users` table (`admin` vs `user`).
   * Include `"role": user.role` in the JWT claims.
   * Add an `@require_role("admin")` decorator to the Resource Server.

---

## License

MIT License. Designed for learning, experimentation, and teaching modern identity architecture.
