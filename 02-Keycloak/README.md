# 🔐 Secure Notes — Keycloak Authentication & RBAC Beginner Project

Welcome to the **Keycloak Secure Notes Application**! This project is a complete, beginner-friendly, production-ready implementation of **Identity & Access Management (IAM)** using **Keycloak** and **Flask (Python)**.

---

## 📚 Table of Contents
1. [What is Keycloak?](#-what-is-keycloak)
2. [Key Concepts Explained](#-key-concepts-explained)
   - [Realms](#1-realms)
   - [Clients](#2-clients)
   - [Roles & RBAC](#3-roles--rbac)
   - [OpenID Connect (OIDC) vs OAuth2](#4-openid-connect-oidc-vs-oauth2)
   - [JSON Web Tokens (JWT)](#5-json-web-tokens-jwt)
3. [Architecture Diagram](#-architecture-diagram)
4. [Prerequisites](#-prerequisites)
5. [Step-by-Step Setup (Windows Commands)](#-step-by-step-setup-windows-commands)
6. [How the Automated Setup Works](#-how-the-automated-setup-works)
7. [Manual Keycloak Setup Guide (Step-by-Step)](#-manual-keycloak-setup-guide-step-by-step)
8. [OAuth2 Authorization Code Flow Explained](#-oauth2-authorization-code-flow-explained)
9. [Security Concepts in This Application](#-security-concepts-in-this-application)
10. [Application Features & Testing Guide](#-application-features--testing-guide)
11. [Common Errors & Troubleshooting](#-common-errors--troubleshooting)
12. [Hands-On Learning Exercises](#-hands-on-learning-exercises)

---

## ❓ What is Keycloak?

**Keycloak** is an open-source Identity and Access Management (IAM) solution maintained by Red Hat and the Cloud Native Computing Foundation (CNCF) community. 

Think of Keycloak as a **centralized passport office and security checkpoint** for your software applications:
- Instead of every web app, mobile app, and API writing its own login forms, password hashing algorithms, password reset emails, and multi-factor authentication (MFA), Keycloak handles all of that centrally.
- When a user wants to log in, your app simply forwards them to Keycloak.
- Keycloak verifies their password, issues a digitally signed badge (a **JSON Web Token**), and sends them back to your app.
- Your app reads the signed token to see who the user is and what permissions they have.

---

## 🔑 Key Concepts Explained

### 1. Realms
A **Realm** is a completely isolated space (a tenant) inside Keycloak. It manages its own collection of users, roles, credentials, and registered applications.
- **`master` Realm:** The special top-level administrative realm. You use it only to manage Keycloak itself and create other realms. Never put your everyday app users here!
- **`notes-app` Realm:** Our dedicated project realm. All users (`testuser`, `admin`), roles, and clients for the Notes app live here.

### 2. Clients
A **Client** is any application or service that delegates user authentication to Keycloak.
- **Confidential Client (Used Here):** Runs on a secure server (like our Flask backend) where a secret key can be safely stored. Keycloak requires both the `client_id` and `client_secret` to exchange codes for tokens.
- **Public Client:** Runs in a public environment where secrets cannot be hidden (e.g., single-page React apps or mobile apps).

### 3. Roles & RBAC
**Role-Based Access Control (RBAC)** assigns permissions to named roles rather than individual users:
- **`user` role:** Grants access to personal notes (`/notes`, `/notes/create`).
- **`admin` role:** Grants access to the system-wide audit portal (`/admin/notes`), allowing administrators to view notes across all accounts.

### 4. OpenID Connect (OIDC) vs OAuth2
- **OAuth 2.0:** An **authorization** framework that answers: *"What is this application allowed to do on behalf of the user?"* (Issues an `access_token`).
- **OpenID Connect (OIDC):** An identity layer built directly on top of OAuth 2.0 that answers: *"Who is the user currently logged in?"* (Issues an `id_token` with user profile claims).

### 5. JSON Web Tokens (JWT)
A **JWT** is a compact, URL-safe string containing three parts separated by dots (`header.payload.signature`):
```text
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMmFiYyIsIm5hbWUiOiJUZXN0IFVzZXIifQ.signature
```
1. **Header:** Algorithm used (e.g., `RS256` - RSA Signature with SHA-256).
2. **Payload:** Data claims about the user (`sub` = unique user ID, `preferred_username`, `email`, `realm_access.roles`).
3. **Signature:** Cryptographically signed by Keycloak's private key. The Flask app verifies the signature using Keycloak's public key, guaranteeing that the token was not tampered with!

---

## 🏗️ Architecture Diagram

```text
+-----------------------------------------------------------------------------------------+
|                                    USER BROWSER                                         |
+-----------------------------------------------------------------------------------------+
         |                                                 ^                     ^
         | 1. Visit http://localhost:5002/login             |                     |
         v                                                 | 4. Redirect with    |
+------------------------------------+                     |    auth code &      |
|         FLASK WEB APP              |                     |    state token      |
|    (Port 5002 - Confidential)      |                     |                     |
|                                    |                     |                     |
|  - Keycloak OIDC Client            |                     |                     |
|  - Token Signature Verification    |                     v                     |
|  - Role-Based Access Control       |         +---------------------------+     |
|  - User Isolation Logic            |         |      KEYCLOAK SERVER      |     |
|  - SQLite (notes.db)               |         |  (Port 8080 - Docker Dev) |     |
+------------------------------------+         |                           |     |
         |                         ^           |  - Realm: notes-app       |     |
         | 5. Backchannel Token    |           |  - Client: notes-client   |     |
         |    Exchange (Code +     | 6. Return |  - Roles: user, admin     |     |
         |    Client Secret)       |    Tokens |  - Users: testuser, admin |     |
         v                         |           +---------------------------+     |
+------------------------------------+                       ^                   |
|       KEYCLOAK TOKEN ENDPOINT      |                       | 2. Redirect to    |
| /realms/notes-app/protocol/openid  |                       |    login form     |
|         -connect/token             |                       +-------------------+
+------------------------------------+
```

---

## 📋 Prerequisites

Before starting, ensure you have installed:
1. **Python 3.10+** (Python 3.11, 3.12, or 3.13)
2. **Docker Desktop** (or Docker Engine with Docker Compose)
3. **Git** (optional, for cloning)
4. A web browser (Edge, Chrome, or Firefox)

---

## 🚀 Step-by-Step Setup (Windows Commands)

Open **PowerShell** or **Command Prompt** and follow these commands:

### Step 1: Open the Project Directory
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\02-Keycloak"
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment in PowerShell
.\venv\Scripts\Activate.ps1

# (Or if using standard CMD):
# .\venv\Scripts\activate.bat
```

> **Note for PowerShell execution policy:** If you encounter a script execution policy restriction, run:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### Step 3: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Start the Keycloak Container
Start the official Keycloak Docker container in development mode:
```powershell
docker compose up -d
```

Verify that the container is running:
```powershell
docker compose ps
```

### Step 5: Run the Automated Keycloak Setup
Wait about 20-30 seconds for Keycloak to finish starting up, then execute:
```powershell
python setup_keycloak.py
```
*The script has built-in retry logic. It will automatically wait for Keycloak to become healthy, create the `notes-app` realm, configure the `notes-client`, create roles, and generate test accounts.*

### Step 6: Initialize the SQLite Database
```powershell
python init_db.py
```

### Step 7: Launch the Flask Web Application
```powershell
python app.py
```

Now open your browser and navigate to:
👉 **[http://localhost:5002](http://localhost:5002)**

---

## 🤖 How the Automated Setup Works

The script `setup_keycloak.py` uses the official Keycloak REST API via the `python-keycloak` library:

1. **Health Polling:** Queries `http://localhost:8080/realms/master` every 3 seconds until Keycloak reports ready.
2. **Admin Authentication:** Authenticates against Keycloak's `master` realm using `admin` / `admin`.
3. **Realm Creation:** Creates the `notes-app` realm with self-registration and email login enabled.
4. **Client Registration:** Registers the confidential client `notes-client`:
   - Redirect URIs: `http://localhost:5002/*` and `http://127.0.0.1:5002/*`
   - Client Secret: `notes-client-secret`
   - Standard Flow (Authorization Code) enabled.
5. **Role Provisioning:** Creates realm roles `user` and `admin`.
6. **User Provisioning:**
   - User `testuser` with password `password` & role `user`.
   - User `admin` with password `password` & roles `admin` and `user`.
   - Sets `temporary=False` so users are not forced to change password on first login.

---

## 🖥️ Manual Keycloak Setup Guide (Step-by-Step)

If you prefer to configure Keycloak manually via its administrative web interface, follow these steps:

### 1. Open the Admin Console
- Open your browser to: **`http://localhost:8080/admin/`**
- Sign in with:
  - **Username:** `admin`
  - **Password:** `admin`

### 2. Create the Realm
- In the top-left dropdown (which currently displays **master**), click **Create Realm**.
- Enter **Realm name:** `notes-app`
- Ensure **Enabled** is toggled **ON**.
- Click **Create**.

### 3. Create the Client
- From the left sidebar, click **Clients**.
- Click the **Create client** button.
- **General Settings:**
  - Client type: `OpenID Connect`
  - Client ID: `notes-client`
  - Name: `Secure Notes Web Client`
  - Click **Next**.
- **Capability config:**
  - Client authentication: Toggle **ON** (this makes it a confidential client).
  - Authorization: Toggle **OFF**.
  - Authentication flow: Check **Standard flow** (Authorization Code Grant) and **Direct access grants**.
  - Click **Next**.
- **Login settings:**
  - Valid redirect URIs: Add `http://localhost:5002/*`
  - Valid post logout redirect URIs: Add `http://localhost:5002/*`
  - Web origins: Add `*`
  - Click **Save**.
- **Retrieve Client Secret:**
  - Click on the **Credentials** tab of your new client.
  - Copy the **Client Secret** (or set it in `.env` to `notes-client-secret`).

### 4. Create Realm Roles
- From the left sidebar, click **Realm roles**.
- Click **Create role**.
  - Role name: `user`
  - Description: `Standard user role`
  - Click **Save**.
- Click **Create role** again:
  - Role name: `admin`
  - Description: `Administrator role`
  - Click **Save**.

### 5. Create Users & Assign Roles
- From the left sidebar, click **Users**.
- Click **Add user**:
  - Username: `testuser`
  - Email: `testuser@example.com`
  - First name: `Test`, Last name: `User`
  - Email verified: Toggle **ON**
  - Click **Create**.
- Go to the **Credentials** tab of `testuser`:
  - Click **Set password**.
  - Password: `password`
  - Password confirmation: `password`
  - Temporary: Toggle **OFF**.
  - Click **Save**.
- Go to the **Role mapping** tab of `testuser`:
  - Click **Assign role**.
  - Filter by realm roles, select `user`, and click **Assign**.
- Repeat the same steps for user `admin`:
  - Username: `admin`, Password: `password`, Temporary: **OFF**.
  - Under **Role mapping**, assign both `admin` and `user` roles.

---

## 🔄 OAuth2 Authorization Code Flow Explained

Here is the exact step-by-step sequence of events when you click **"Sign In with Keycloak"**:

```text
Step 1: User clicks "Sign In"
        App creates random state: "xK9#mQ2..."
        Redirects browser to Keycloak:
        GET /realms/notes-app/protocol/openid-connect/auth?
            client_id=notes-client&
            redirect_uri=http://localhost:5002/callback&
            response_type=code&
            scope=openid profile email&
            state=xK9#mQ2...

Step 2: Keycloak renders login form
        User enters username & password
        Keycloak verifies credentials in realm

Step 3: Keycloak redirects back to Flask
        GET http://localhost:5002/callback?
            code=7b203c80-e889-4b68-b86a-74...&
            state=xK9#mQ2...

Step 4: Flask verifies state
        Does state match session['oauth_state']? 
        YES -> Protects against Cross-Site Request Forgery (CSRF).

Step 5: Flask calls Keycloak Token Endpoint (Backchannel)
        POST http://localhost:8080/realms/notes-app/protocol/openid-connect/token
        Payload:
            grant_type = authorization_code
            code = 7b203c80-e889-4b68-b86a-74...
            client_id = notes-client
            client_secret = notes-client-secret
            redirect_uri = http://localhost:5002/callback

Step 6: Keycloak returns Tokens
        {
           "access_token": "eyJhbGciOiJSUzI1NiIs...",
           "id_token": "eyJhbGciOiJSUzI1NiIs...",
           "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
           "expires_in": 300
        }

Step 7: Flask decodes JWT & stores session
        Extracts user UUID (sub), username, and roles ['user'].
        Redirects user to /notes.
```

---

## 🛡️ Security Concepts in This Application

1. **No Passwords in the Web App:** The Flask application never sees, collects, or hashes user passwords. Passwords remain safely inside Keycloak.
2. **State Parameter (CSRF Defense):** Before redirecting to Keycloak, Flask generates a cryptographically secure random token (`secrets.token_urlsafe(32)`). When Keycloak redirects back, Flask validates this token before exchanging the code.
3. **Cryptographic Token Verification:** Tokens are cryptographically validated using Keycloak's public keys (JWKS). Tampered tokens are immediately rejected.
4. **Data Isolation (Tenant Separation):** Every note in the SQLite database is linked to the user's immutable Keycloak Subject ID (`sub`). Even if user `testuser` changes their displayed username, their notes remain strictly tied to their account.
5. **Single Sign-Out (RP-Initiated Logout):** When clicking "Sign Out", the app not only destroys the local Flask session cookie, but also redirects the browser to Keycloak's OIDC logout endpoint (`id_token_hint` parameter). This ensures the user is logged out of the central Single Sign-On session.

---

## 🧪 Application Features & Testing Guide

### Test Case 1: Standard User Permissions
1. Go to `http://localhost:5002/` and click **"Sign In with Keycloak"**.
2. Log in as:
   - **Username:** `testuser`
   - **Password:** `password`
3. Notice your username and `<User>` role badge in the navigation bar.
4. Click **"+ New Note"** and create a personal note:
   - Title: `My Secret Recipe`
   - Content: `Grandma's secret sauce recipe.`
5. Go to **"My Notes"**. You will see your note.
6. Try visiting the Admin Dashboard directly by typing `http://localhost:5002/admin/notes` in the browser URL bar.
7. **Expected Result:** You will receive a **`403 Forbidden`** error because your account only has the `user` role!

---

### Test Case 2: Administrator Auditing
1. Click **"Sign Out"**.
2. Click **"Sign In with Keycloak"** and log in as:
   - **Username:** `admin`
   - **Password:** `password`
3. Notice your `<Admin>` role badge in the navigation bar.
4. Click the purple **"Admin Dashboard"** link in the navigation bar.
5. **Expected Result:** You will see the administrative dashboard listing **all notes** across all users (including `testuser`'s notes and system statistics).

---

### Test Case 3: Single Sign-Out Verification
1. While logged in as `admin`, click **"Sign Out"**.
2. You will be redirected back to the home page with a confirmation banner.
3. Attempt to navigate directly to `http://localhost:5002/notes`.
4. **Expected Result:** You will be automatically intercepted and redirected to the login page.

---

## 🛠️ Common Errors & Troubleshooting

### 1. `Invalid parameter: redirect_uri`
- **Cause:** Keycloak received a redirect URI that does not match the allowed list configured in the client.
- **Fix:** In Keycloak Admin Console $\rightarrow$ Clients $\rightarrow$ `notes-client` $\rightarrow$ Valid redirect URIs, make sure `http://localhost:5002/*` and `http://127.0.0.1:5002/*` are present.

### 2. `Connection refused: http://localhost:8080`
- **Cause:** Docker container is still booting or not running.
- **Fix:** Check `docker compose ps`. If container is stopped, run `docker compose up -d`. Keycloak takes about 20-30 seconds to initialize Quarkus.

### 3. `Port 8080 or Port 5002 is already in use`
- **Cause:** Another service (like Apache, Jenkins, or an old Flask process) is occupying port 8080 or 5002.
- **Fix (Windows):** Find and terminate the process holding the port:
  ```powershell
  # Find PID using port 5002
  netstat -ano | findstr :5002
  # Terminate process by PID
  taskkill /PID <PID> /F
  ```

### 4. `Invalid parameter: post_logout_redirect_uri`
- **Cause:** The post-logout redirect URI is not registered in the client settings.
- **Fix:** In `notes-client` configuration, add `http://localhost:5002/*` to **Valid post logout redirect URIs**.

---

## 🎓 Hands-On Learning Exercises

Try completing these exercises to deepen your understanding:

1. **Exercise 1: Add User Self-Registration**
   - In Keycloak Admin Console, go to **Realm Settings** $\rightarrow$ **Login**.
   - Enable **User registration**.
   - Log out of your app and click **Sign In**. Notice the new "Register" link on Keycloak's login form. Register a brand new user and see how default roles are assigned!

2. **Exercise 2: Implement Note Editing**
   - Add a route `/notes/edit/<int:note_id>` in `app.py`.
   - Ensure a regular user can only edit their own note, while an admin cannot alter other users' notes without an explicit audit flag.

3. **Exercise 3: Inspect Token in jwt.io**
   - In `app.py`, add a print statement to output `tokens['access_token']`.
   - Copy the string and paste it into [jwt.io](https://jwt.io).
   - Inspect the decoded header, payload claims, issuer (`iss`), and expiration timestamp (`exp`).

---

## 📄 License
This project is open-source and intended for educational and reference purposes.
