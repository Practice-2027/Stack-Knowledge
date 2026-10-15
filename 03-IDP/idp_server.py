"""
idp_server.py
=============
Custom Identity Provider (IDP) Server built with Flask.
Runs on Port 5003.

Core Responsibilities:
1. User Management & Authentication (Registration, Login, Password Hashing).
2. Token Issuance (OAuth 2.0 Authorization Code flow & Token Exchange).
3. JWT Signing using RSA-256 (RS256 asymmetric cryptography).
4. Public Key Distribution via JWKS (/jwks) and OIDC Discovery (/.well-known/openid-configuration).
5. Userinfo Endpoint (/userinfo) for standard identity retrieval.
"""

import os
import sys
import time
import json
import sqlite3
import secrets
from datetime import datetime, timezone

from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from cryptography.hazmat.primitives import serialization

# Ensure helper modules in current folder can be imported
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from generate_keys import ensure_keys_exist, PRIVATE_KEY_PATH, PUBLIC_KEY_PATH

# ---------------------------------------------------------
# Flask App Configuration
# ---------------------------------------------------------
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.config["SECRET_KEY"] = secrets.token_hex(32)
CORS(app)  # Allow cross-origin requests for API consumers

DB_PATH = os.path.join(BASE_DIR, "idp_database.db")
KEY_ID = "idp-key-1"  # Identifier for the RSA key in the JWKS
ISSUER = "http://localhost:5003"
ACCESS_TOKEN_LIFETIME = 900        # 15 minutes (short-lived for security)
REFRESH_TOKEN_LIFETIME = 604800   # 7 days
AUTH_CODE_LIFETIME = 300          # 5 minutes

# ---------------------------------------------------------
# RSA Keys Loading
# ---------------------------------------------------------
ensure_keys_exist()

with open(PRIVATE_KEY_PATH, "rb") as f:
    PRIVATE_KEY_PEM = f.read()

with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY_PEM = f.read()

# Load cryptography objects
private_key_obj = serialization.load_pem_private_key(PRIVATE_KEY_PEM, password=None)
public_key_obj = serialization.load_pem_public_key(PUBLIC_KEY_PEM)


# ---------------------------------------------------------
# Database Initialization & Helpers
# ---------------------------------------------------------
def get_db():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite schema and seeds default users/clients."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # OAuth Clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id TEXT PRIMARY KEY,
            client_secret TEXT NOT NULL,
            client_name TEXT NOT NULL,
            redirect_uris TEXT NOT NULL
        )
    """)

    # Authorization Codes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_codes (
            code TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            redirect_uri TEXT NOT NULL,
            username TEXT NOT NULL,
            scope TEXT NOT NULL,
            expires_at REAL NOT NULL,
            used INTEGER DEFAULT 0
        )
    """)

    # Refresh Tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            client_id TEXT NOT NULL,
            scope TEXT NOT NULL,
            expires_at REAL NOT NULL,
            revoked INTEGER DEFAULT 0
        )
    """)

    # Seed demo users if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        print("[IDP:5003] Seeding demo users: 'alice' and 'bob'...")
        demo_users = [
            ("alice", "alice@example.com", generate_password_hash("password123"), "Alice Smith"),
            ("bob", "bob@example.com", generate_password_hash("secret456"), "Bob Jones")
        ]
        cursor.executemany(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            demo_users
        )

    # Seed demo OAuth client if not exists
    cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id = ?", ("client_app_demo",))
    if cursor.fetchone()[0] == 0:
        print("[IDP:5003] Registering demo client: 'client_app_demo'...")
        cursor.execute(
            "INSERT INTO clients (client_id, client_secret, client_name, redirect_uris) VALUES (?, ?, ?, ?)",
            (
                "client_app_demo",
                "super-secret-client-password",
                "Demo Client Application",
                "http://localhost:5005/callback,http://127.0.0.1:5005/callback"
            )
        )

    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------------
# JWT & Token Helper Functions
# ---------------------------------------------------------
def create_access_token(user_dict, scope="openid profile email", audience="resource_server"):
    """
    Creates an RS256 signed JSON Web Token (JWT).
    The token includes standard RFC 7519 claims:
      - iss: Issuer URL (who created the token)
      - sub: Subject (username / user identifier)
      - aud: Audience (which server is meant to consume this token)
      - exp: Expiration time (unix timestamp)
      - iat: Issued at time (unix timestamp)
      - custom claims: email, name, scope
    """
    now = int(time.time())
    payload = {
        "iss": ISSUER,
        "sub": user_dict["username"],
        "aud": audience,
        "iat": now,
        "exp": now + ACCESS_TOKEN_LIFETIME,
        "user_id": user_dict["id"],
        "email": user_dict["email"],
        "name": user_dict.get("full_name") or user_dict["username"],
        "scope": scope
    }

    headers = {
        "kid": KEY_ID,
        "alg": "RS256",
        "typ": "JWT"
    }

    token = jwt.encode(payload, private_key_obj, algorithm="RS256", headers=headers)
    return token


def create_id_token(user_dict, client_id):
    """Creates an OpenID Connect ID Token intended for the client app."""
    now = int(time.time())
    payload = {
        "iss": ISSUER,
        "sub": user_dict["username"],
        "aud": client_id,
        "iat": now,
        "exp": now + ACCESS_TOKEN_LIFETIME,
        "email": user_dict["email"],
        "name": user_dict.get("full_name") or user_dict["username"]
    }
    headers = {"kid": KEY_ID, "alg": "RS256", "typ": "JWT"}
    return jwt.encode(payload, private_key_obj, algorithm="RS256", headers=headers)


def create_refresh_token(username, client_id, scope):
    """Creates and stores a cryptographically secure refresh token in SQLite."""
    token = secrets.token_urlsafe(48)
    expires_at = time.time() + REFRESH_TOKEN_LIFETIME

    conn = get_db()
    conn.execute(
        "INSERT INTO refresh_tokens (token, username, client_id, scope, expires_at) VALUES (?, ?, ?, ?, ?)",
        (token, username, client_id, scope, expires_at)
    )
    conn.commit()
    conn.close()
    return token


def verify_bearer_token(auth_header):
    """
    Extracts and validates a Bearer token from the Authorization header.
    Returns decoded payload dict or None.
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Missing or invalid Authorization header format"

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(
            token,
            public_key_obj,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={"verify_aud": False}  # userinfo endpoint accepts any valid audience
        )
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Root info endpoint explaining the IDP status."""
    return jsonify({
        "service": "Custom Identity Provider (IDP)",
        "status": "online",
        "port": 5003,
        "discovery_url": f"{ISSUER}/.well-known/openid-configuration",
        "jwks_url": f"{ISSUER}/jwks",
        "authorize_url": f"{ISSUER}/authorize",
        "token_url": f"{ISSUER}/token"
    })


@app.route("/.well-known/openid-configuration", methods=["GET"])
def openid_configuration():
    """
    OpenID Connect Discovery 1.0 Endpoint.
    Clients query this standard URL to automatically discover OAuth2/OIDC endpoints and capabilities.
    """
    print("[IDP:5003] OIDC Discovery configuration requested")
    config = {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "token_refresh_endpoint": f"{ISSUER}/token/refresh",
        "userinfo_endpoint": f"{ISSUER}/userinfo",
        "jwks_uri": f"{ISSUER}/jwks",
        "registration_endpoint": f"{ISSUER}/register",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email", "read", "write"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
        "claims_supported": ["sub", "iss", "aud", "exp", "iat", "email", "name", "scope"]
    }
    return jsonify(config)


@app.route("/jwks", methods=["GET"])
def jwks():
    """
    JSON Web Key Set (JWKS) Endpoint.
    Publishes the IDP's RSA public keys in standard JWK format.
    Resource servers and clients use this to verify JWT signatures WITHOUT needing the private key!
    """
    print("[IDP:5003] JWKS requested by client/resource server")
    # Export RSA public key parameters to JWK dict
    jwk_dict = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key_obj))
    jwk_dict["kid"] = KEY_ID
    jwk_dict["use"] = "sig"      # Intended for signature verification
    jwk_dict["alg"] = "RS256"

    return jsonify({"keys": [jwk_dict]})


@app.route("/register", methods=["POST"])
def register():
    """
    User Registration Endpoint.
    Accepts JSON or Form data with username, email, password, and optional full_name.
    Stores user in SQLite with salted password hash using Werkzeug.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or username).strip()

    if not username or not email or not password:
        return jsonify({"error": "invalid_request", "error_description": "username, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "invalid_password", "error_description": "password must be at least 6 characters"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Check for existing username or email
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "user_exists", "error_description": "Username or email is already registered"}), 409

    pwd_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
        (username, email, pwd_hash, full_name)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    print(f"[IDP:5003] User registered successfully: id={new_id}, username='{username}'")
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_id,
            "username": username,
            "email": email,
            "full_name": full_name
        }
    }), 201


@app.route("/login", methods=["POST"])
def login():
    """
    Direct User Login Endpoint (Resource Owner Password style).
    Accepts JSON or Form data with username and password.
    Returns access_token (JWT), refresh_token, and user info.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "invalid_request", "error_description": "username and password are required"}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        print(f"[IDP:5003] Failed login attempt for username='{username}'")
        return jsonify({"error": "invalid_credentials", "error_description": "Invalid username or password"}), 401

    user_dict = dict(user)
    access_token = create_access_token(user_dict, scope="openid profile email read write")
    refresh_token = create_refresh_token(user_dict["username"], "direct_login", "openid profile email")

    print(f"[IDP:5003] User logged in: username='{username}'. Issued access and refresh tokens.")
    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_LIFETIME,
        "refresh_token": refresh_token,
        "user": {
            "id": user_dict["id"],
            "username": user_dict["username"],
            "email": user_dict["email"],
            "full_name": user_dict["full_name"]
        }
    })


@app.route("/token/refresh", methods=["POST"])
def refresh_token_endpoint():
    """
    Dedicated Refresh Token Endpoint.
    Accepts JSON or Form data: { "refresh_token": "..." }.
    Validates token in SQLite and issues a brand new access token.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    r_token = data.get("refresh_token")

    if not r_token:
        return jsonify({"error": "invalid_request", "error_description": "refresh_token parameter is required"}), 400

    conn = get_db()
    row = conn.execute("SELECT * FROM refresh_tokens WHERE token = ?", (r_token,)).fetchone()

    if not row:
        conn.close()
        print("[IDP:5003] Refresh token not found")
        return jsonify({"error": "invalid_grant", "error_description": "Invalid refresh token"}), 400

    if row["revoked"] == 1:
        conn.close()
        print("[IDP:5003] Attempted to use revoked refresh token")
        return jsonify({"error": "invalid_grant", "error_description": "Refresh token has been revoked"}), 400

    if row["expires_at"] < time.time():
        conn.close()
        print("[IDP:5003] Attempted to use expired refresh token")
        return jsonify({"error": "invalid_grant", "error_description": "Refresh token has expired"}), 400

    # Token is valid! Fetch user
    user = conn.execute("SELECT * FROM users WHERE username = ?", (row["username"],)).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "invalid_grant", "error_description": "User no longer exists"}), 400

    user_dict = dict(user)
    new_access_token = create_access_token(user_dict, scope=row["scope"])

    print(f"[IDP:5003] Issued new access token via refresh token for user='{row['username']}'")
    return jsonify({
        "access_token": new_access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_LIFETIME,
        "scope": row["scope"]
    })


@app.route("/authorize", methods=["GET", "POST"])
def authorize():
    """
    OAuth 2.0 Authorization Endpoint.
    GET:
      - Validates query params (client_id, redirect_uri, response_type).
      - Displays login & authorization consent screen to the end-user.
    POST:
      - Authenticates user credentials or handles new registration.
      - Generates an authorization code.
      - Redirects browser back to redirect_uri with code and state.
    """
    if request.method == "GET":
        client_id = request.args.get("client_id", "")
        redirect_uri = request.args.get("redirect_uri", "")
        response_type = request.args.get("response_type", "code")
        scope = request.args.get("scope", "openid profile email read write")
        state = request.args.get("state", "")

        print(f"[IDP:5003] Authorization GET request for client_id='{client_id}', redirect_uri='{redirect_uri}'")

        # Validate client_id
        conn = get_db()
        client = conn.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,)).fetchone()
        conn.close()

        if not client:
            return f"<h3>OAuth Error: Invalid client_id '{client_id}'</h3>", 400

        if response_type != "code":
            return f"<h3>OAuth Error: Unsupported response_type '{response_type}'. Only 'code' is supported.</h3>", 400

        # Render login form with parameters
        return render_template(
            "login_form.html",
            client_id=client_id,
            redirect_uri=redirect_uri,
            response_type=response_type,
            scope=scope,
            state=state
        )

    # POST - Handle Login or Registration Submission
    action = request.form.get("action", "login")
    client_id = request.form.get("client_id", "")
    redirect_uri = request.form.get("redirect_uri", "")
    response_type = request.form.get("response_type", "code")
    scope = request.form.get("scope", "openid profile email read write")
    state = request.form.get("state", "")

    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,)).fetchone()

    if not client:
        conn.close()
        return "<h3>OAuth Error: Invalid client</h3>", 400

    authenticated_user = None

    if action == "register":
        # Handle registration inside authorization screen
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        full_name = (request.form.get("full_name") or username).strip()

        if not username or not email or not password:
            conn.close()
            return render_template(
                "login_form.html",
                error="All registration fields are required.",
                client_id=client_id, redirect_uri=redirect_uri, scope=scope, state=state
            ), 400

        # Check existing
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            return render_template(
                "login_form.html",
                error="Username or email is already taken.",
                client_id=client_id, redirect_uri=redirect_uri, scope=scope, state=state
            ), 400

        pwd_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (username, email, pwd_hash, full_name)
        )
        conn.commit()
        authenticated_user = {"id": cursor.lastrowid, "username": username, "email": email, "full_name": full_name}
        print(f"[IDP:5003] New user registered during auth flow: '{username}'")

    else:
        # Standard login
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user_row or not check_password_hash(user_row["password_hash"], password):
            conn.close()
            print(f"[IDP:5003] Invalid credentials submitted for username='{username}'")
            return render_template(
                "login_form.html",
                error="Invalid username or password. Please try again.",
                client_id=client_id, redirect_uri=redirect_uri, scope=scope, state=state
            ), 401

        authenticated_user = dict(user_row)

    # Generate Authorization Code
    auth_code = secrets.token_urlsafe(32)
    expires_at = time.time() + AUTH_CODE_LIFETIME

    conn.execute(
        """INSERT INTO auth_codes (code, client_id, redirect_uri, username, scope, expires_at, used)
           VALUES (?, ?, ?, ?, ?, ?, 0)""",
        (auth_code, client_id, redirect_uri, authenticated_user["username"], scope, expires_at)
    )
    conn.commit()
    conn.close()

    print(f"[IDP:5003] Generated auth code for user='{authenticated_user['username']}' -> redirecting to client")

    # Redirect user's browser back to client application
    delimiter = "&" if "?" in redirect_uri else "?"
    redirect_target = f"{redirect_uri}{delimiter}code={auth_code}"
    if state:
        redirect_target += f"&state={state}"

    return redirect(redirect_target, code=302)


@app.route("/token", methods=["POST"])
def token():
    """
    OAuth 2.0 Token Endpoint.
    Handles:
      1. grant_type="authorization_code": Exchanges auth code for access token, refresh token, & id_token.
      2. grant_type="refresh_token": Exchanges refresh token for new access token.
    Accepts application/x-www-form-urlencoded or application/json.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    grant_type = data.get("grant_type")

    print(f"[IDP:5003] POST /token received with grant_type='{grant_type}'")

    conn = get_db()

    # Case 1: Authorization Code Exchange
    if grant_type == "authorization_code":
        code = data.get("code")
        client_id = data.get("client_id")
        redirect_uri = data.get("redirect_uri")

        if not code or not client_id:
            conn.close()
            return jsonify({"error": "invalid_request", "error_description": "code and client_id are required"}), 400

        # Query code record
        row = conn.execute("SELECT * FROM auth_codes WHERE code = ?", (code,)).fetchone()

        if not row:
            conn.close()
            print(f"[IDP:5003] Auth code not found: '{code}'")
            return jsonify({"error": "invalid_grant", "error_description": "Invalid authorization code"}), 400

        if row["used"] == 1:
            conn.close()
            print(f"[IDP:5003] Auth code already used: '{code}' (preventing replay attack)")
            return jsonify({"error": "invalid_grant", "error_description": "Authorization code has already been used"}), 400

        if row["expires_at"] < time.time():
            conn.close()
            print(f"[IDP:5003] Auth code expired: '{code}'")
            return jsonify({"error": "invalid_grant", "error_description": "Authorization code has expired"}), 400

        if row["client_id"] != client_id:
            conn.close()
            return jsonify({"error": "invalid_grant", "error_description": "Client ID does not match code"}), 400

        # Mark code as USED immediately
        conn.execute("UPDATE auth_codes SET used = 1 WHERE code = ?", (code,))
        conn.commit()

        # Fetch user
        user = conn.execute("SELECT * FROM users WHERE username = ?", (row["username"],)).fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "invalid_grant", "error_description": "User associated with code not found"}), 400

        user_dict = dict(user)
        access_token = create_access_token(user_dict, scope=row["scope"])
        id_token = create_id_token(user_dict, client_id)
        refresh_token = create_refresh_token(user_dict["username"], client_id, row["scope"])

        print(f"[IDP:5003] Auth code successfully exchanged! Issued access_token, id_token, refresh_token for '{user_dict['username']}'")

        return jsonify({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_LIFETIME,
            "refresh_token": refresh_token,
            "id_token": id_token,
            "scope": row["scope"]
        })

    # Case 2: Refresh Token Grant
    elif grant_type == "refresh_token":
        r_token = data.get("refresh_token")
        if not r_token:
            conn.close()
            return jsonify({"error": "invalid_request", "error_description": "refresh_token is required"}), 400

        row = conn.execute("SELECT * FROM refresh_tokens WHERE token = ?", (r_token,)).fetchone()
        if not row or row["revoked"] == 1 or row["expires_at"] < time.time():
            conn.close()
            return jsonify({"error": "invalid_grant", "error_description": "Invalid, expired, or revoked refresh token"}), 400

        user = conn.execute("SELECT * FROM users WHERE username = ?", (row["username"],)).fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "invalid_grant", "error_description": "User not found"}), 400

        user_dict = dict(user)
        new_access_token = create_access_token(user_dict, scope=row["scope"])

        print(f"[IDP:5003] Refresh token exchanged for new access token for user='{user_dict['username']}'")
        return jsonify({
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_LIFETIME,
            "scope": row["scope"]
        })

    else:
        conn.close()
        return jsonify({
            "error": "unsupported_grant_type",
            "error_description": f"Grant type '{grant_type}' is not supported. Use 'authorization_code' or 'refresh_token'."
        }), 400


@app.route("/userinfo", methods=["GET", "POST"])
def userinfo():
    """
    OpenID Connect UserInfo Endpoint.
    Clients supply the Bearer access token in the Authorization header.
    Returns JSON profile claims about the authenticated subject.
    """
    auth_header = request.headers.get("Authorization")
    payload, err = verify_bearer_token(auth_header)

    if err:
        print(f"[IDP:5003] /userinfo unauthorized: {err}")
        return jsonify({"error": "invalid_token", "error_description": err}), 401

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (payload["sub"],)).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "not_found", "error_description": "User not found"}), 404

    print(f"[IDP:5003] /userinfo called successfully for user='{user['username']}'")
    return jsonify({
        "sub": user["username"],
        "username": user["username"],
        "email": user["email"],
        "name": user["full_name"],
        "email_verified": True,
        "updated_at": int(time.time())
    })


# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("        CUSTOM IDENTITY PROVIDER (IDP) STARTING ON PORT 5003    ")
    print("=" * 65)
    print(f" * Base URL:            {ISSUER}")
    print(f" * OIDC Discovery:      {ISSUER}/.well-known/openid-configuration")
    print(f" * JWKS Key Set:        {ISSUER}/jwks")
    print(f" * Authorize URL:       {ISSUER}/authorize")
    print(f" * Token URL:           {ISSUER}/token")
    print(f" * UserInfo URL:        {ISSUER}/userinfo")
    print(f" * Registered Demo Client: client_app_demo")
    print(f" * Demo User 1:         alice / password123")
    print(f" * Demo User 2:         bob / secret456")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5003, debug=False)
