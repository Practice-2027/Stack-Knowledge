"""
=============================================================================
Mock Keycloak Server (Standalone Fallback on Port 8088)
=============================================================================
Provides a fully functional OpenID Connect (OIDC) Identity Provider that mimics
Red Hat Keycloak for local testing when Docker Desktop is not running.

Endpoints implemented:
- GET  /                                             : Welcome & Admin Portal
- GET  /realms/notes-app/.well-known/openid-configuration : OIDC Discovery
- GET  /realms/notes-app/protocol/openid-connect/certs     : JWKS Public Keys
- GET  /realms/notes-app/protocol/openid-connect/auth      : SSO Login Screen
- POST /realms/notes-app/protocol/openid-connect/auth      : Process Login & Issue Auth Code
- POST /realms/notes-app/protocol/openid-connect/token     : Token Exchange
- GET  /realms/notes-app/protocol/openid-connect/userinfo  : User Info
- GET  /realms/notes-app/protocol/openid-connect/logout    : Single Sign-Out
=============================================================================
"""

import base64
import os
import secrets
import time
import uuid
import jwt
from flask import Flask, jsonify, redirect, render_template_string, request
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)
PORT = int(os.environ.get("KEYCLOAK_PORT", 8088))
BASE_URL = f"http://localhost:{PORT}"
REALM = "notes-app"

# -----------------------------------------------------------------------------
# Generate RSA Key Pair for Token Signing
# -----------------------------------------------------------------------------
_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_private_pem = _private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
_public_key = _private_key.public_key()
_public_numbers = _public_key.public_numbers()

def int_to_base64url(val):
    byte_len = (val.bit_length() + 7) // 8
    val_bytes = val.to_bytes(byte_len, byteorder="big")
    return base64.urlsafe_b64encode(val_bytes).rstrip(b"=").decode("ascii")

KID = "mock-keycloak-key-1"
JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": KID,
            "n": int_to_base64url(_public_numbers.n),
            "e": int_to_base64url(_public_numbers.e),
        }
    ]
}

# In-memory storage for authorization codes and sessions
AUTH_CODES = {}

USERS = {
    "testuser": {
        "password": "password",
        "roles": ["user"],
        "name": "Regular Test User",
        "email": "testuser@example.com",
        "sub": "user-uuid-1111-2222-3333",
    },
    "admin": {
        "password": "password",
        "roles": ["admin", "user"],
        "name": "System Administrator",
        "email": "admin@example.com",
        "sub": "admin-uuid-4444-5555-6666",
    },
}

LOGIN_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Keycloak Single Sign-On</title>
    <meta charset="utf-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 32px; width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .logo { text-align: center; font-size: 24px; font-weight: bold; color: #38bdf8; margin-bottom: 8px; }
        .subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-bottom: 24px; }
        .badge { background: #0369a1; color: #e0f2fe; padding: 4px 10px; border-radius: 999px; font-size: 12px; display: inline-block; }
        .form-group { margin-bottom: 16px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #cbd5e1; margin-bottom: 6px; }
        input, select { width: 100%; box-sizing: border-box; padding: 10px 14px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 14px; }
        button { width: 100%; padding: 12px; border-radius: 6px; border: none; background: #0284c7; color: white; font-size: 15px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { background: #0369a1; }
        .demo-box { margin-top: 20px; padding: 12px; background: #0f172a; border-radius: 6px; font-size: 12px; border: 1px dashed #475569; }
        .demo-box code { color: #38bdf8; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">🛡️ Keycloak Identity</div>
        <div class="subtitle"><span class="badge">Realm: {{ realm }}</span></div>
        <form method="POST">
            <input type="hidden" name="redirect_uri" value="{{ redirect_uri }}">
            <input type="hidden" name="state" value="{{ state }}">
            <div class="form-group">
                <label>Username</label>
                <select name="username" id="user-select" onchange="document.getElementById('pwd').value='password'">
                    <option value="testuser">testuser (Role: user)</option>
                    <option value="admin">admin (Role: admin, user)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" id="pwd" value="password" required>
            </div>
            <button type="submit">Sign In via Keycloak</button>
        </form>
        <div class="demo-box">
            <strong>Pre-configured Accounts:</strong><br>
            • <code>testuser</code> / <code>password</code> (Standard Notes)<br>
            • <code>admin</code> / <code>password</code> (Admin Audit Access)
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return jsonify({
        "server": "Mock Keycloak OIDC Server",
        "realm": REALM,
        "status": "online",
        "discovery": f"{BASE_URL}/realms/{REALM}/.well-known/openid-configuration",
        "certs": f"{BASE_URL}/realms/{REALM}/protocol/openid-connect/certs",
    })

@app.route(f"/realms/{REALM}/.well-known/openid-configuration")
def openid_config():
    realm_base = f"{BASE_URL}/realms/{REALM}"
    return jsonify({
        "issuer": realm_base,
        "authorization_endpoint": f"{realm_base}/protocol/openid-connect/auth",
        "token_endpoint": f"{realm_base}/protocol/openid-connect/token",
        "userinfo_endpoint": f"{realm_base}/protocol/openid-connect/userinfo",
        "end_session_endpoint": f"{realm_base}/protocol/openid-connect/logout",
        "jwks_uri": f"{realm_base}/protocol/openid-connect/certs",
        "response_types_supported": ["code", "none", "id_token", "token"],
        "subject_types_supported": ["public", "pairwise"],
        "id_token_signing_alg_values_supported": ["RS256"],
    })

@app.route(f"/realms/{REALM}/protocol/openid-connect/certs")
def certs():
    return jsonify(JWKS)

@app.route(f"/realms/{REALM}/protocol/openid-connect/auth", methods=["GET", "POST"])
def auth():
    if request.method == "GET":
        redirect_uri = request.args.get("redirect_uri", "http://localhost:5002/callback")
        state = request.args.get("state", "")
        return render_template_string(LOGIN_HTML, realm=REALM, redirect_uri=redirect_uri, state=state)
    
    username = request.form.get("username", "testuser")
    redirect_uri = request.form.get("redirect_uri", "http://localhost:5002/callback")
    state = request.form.get("state", "")
    
    code = secrets.token_urlsafe(16)
    AUTH_CODES[code] = {
        "username": username,
        "expires_at": time.time() + 300,
    }
    
    delimiter = "&" if "?" in redirect_uri else "?"
    target = f"{redirect_uri}{delimiter}code={code}&state={state}"
    return redirect(target)

@app.route(f"/realms/{REALM}/protocol/openid-connect/token", methods=["POST"])
def token_endpoint():
    grant_type = request.form.get("grant_type", "authorization_code")
    username = "testuser"
    
    if grant_type == "authorization_code":
        code = request.form.get("code")
        if code in AUTH_CODES:
            entry = AUTH_CODES.pop(code)
            username = entry["username"]
    elif grant_type == "refresh_token":
        username = request.form.get("username", "testuser")
        
    user = USERS.get(username, USERS["testuser"])
    now = int(time.time())
    
    claims = {
        "iss": f"{BASE_URL}/realms/{REALM}",
        "sub": user["sub"],
        "aud": "notes-client",
        "exp": now + 3600,
        "iat": now,
        "preferred_username": username,
        "email": user["email"],
        "name": user["name"],
        "realm_access": {"roles": user["roles"]},
        "resource_access": {"notes-client": {"roles": user["roles"]}},
    }
    
    token = jwt.encode(claims, _private_pem, algorithm="RS256", headers={"kid": KID})
    refresh = secrets.token_urlsafe(32)
    id_token = token
    
    return jsonify({
        "access_token": token,
        "refresh_token": refresh,
        "id_token": id_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_expires_in": 86400,
    })

@app.route(f"/realms/{REALM}/protocol/openid-connect/userinfo")
def userinfo():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    try:
        decoded = jwt.decode(token, _public_key, algorithms=["RS256"], audience="notes-client")
        return jsonify({
            "sub": decoded.get("sub"),
            "preferred_username": decoded.get("preferred_username"),
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "roles": decoded.get("realm_access", {}).get("roles", ["user"]),
        })
    except Exception:
        return jsonify({
            "sub": "user-uuid-1111",
            "preferred_username": "testuser",
            "email": "testuser@example.com",
            "roles": ["user"]
        })

@app.route(f"/realms/{REALM}/protocol/openid-connect/logout", methods=["GET", "POST"])
def logout():
    redirect_uri = request.args.get("post_logout_redirect_uri", "http://localhost:5002/")
    return redirect(redirect_uri)

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print(f"  🛡️ Mock Keycloak Server running on {BASE_URL}")
    print(f"  Realm: {REALM}")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
