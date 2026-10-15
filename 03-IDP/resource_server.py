"""
resource_server.py
==================
Protected API / Resource Server built with Flask.
Runs on Port 5004.

Core Responsibilities:
1. Protects private resources (profiles, private data, documents).
2. Validates JWT access tokens independently using IDP's public JWKS.
3. Does NOT require any shared secrets or private keys!
4. Enforces token expiration, cryptographic RS256 signature, issuer, and scopes.
5. Returns proper HTTP 401 Unauthorized / 403 Forbidden responses.
"""

import os
import sys
import time
import json
import sqlite3
import functools
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt

# ---------------------------------------------------------
# Flask App Configuration
# ---------------------------------------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "resource_database.db")

IDP_BASE_URL = os.environ.get("IDP_BASE_URL", "http://localhost:5003")
JWKS_URL = f"{IDP_BASE_URL}/jwks"
EXPECTED_ISSUER = IDP_BASE_URL
EXPECTED_AUDIENCE = "resource_server"

# Cache for public keys retrieved from JWKS: kid -> public_key_obj
JWKS_CACHE = {}
JWKS_CACHE_EXPIRY = 0
CACHE_TTL = 300  # 5 minutes


# ---------------------------------------------------------
# SQLite Database for User Resources
# ---------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed initial documents if empty
    cursor.execute("SELECT COUNT(*) FROM user_documents")
    if cursor.fetchone()[0] == 0:
        print("[RESOURCE:5004] Seeding initial protected documents...")
        initial_docs = [
            ("alice", "Project Apollo Architecture Specs", "Confidential system design docs for next-generation federated identity.", "Engineering"),
            ("alice", "Security Audit Checklist", "Zero-trust verification, RS256 signature validation, and token rotation rules.", "Security"),
            ("bob", "Q4 Financial Forecasts", "Audited quarterly projections, ledger reconciliations, and department budgets.", "Finance"),
            ("bob", "Supplier Contract Review", "Master service agreements and confidential vendor rate cards.", "Legal")
        ]
        cursor.executemany(
            "INSERT INTO user_documents (username, title, content, category) VALUES (?, ?, ?, ?)",
            initial_docs
        )
    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------------
# JWKS & Token Validation Logic
# ---------------------------------------------------------
def get_signing_key(kid):
    """
    Retrieves the RSA public key for a given Key ID (kid) from the IDP's JWKS.
    Caches keys locally to prevent making an HTTP call on every request.
    """
    global JWKS_CACHE, JWKS_CACHE_EXPIRY

    now = time.time()
    # Check if key is already cached and cache is fresh
    if kid in JWKS_CACHE and now < JWKS_CACHE_EXPIRY:
        return JWKS_CACHE[kid]

    print(f"[RESOURCE:5004] Fetching fresh JWKS from IDP: {JWKS_URL}...")
    try:
        response = requests.get(JWKS_URL, timeout=5)
        response.raise_for_status()
        jwks_data = response.json()

        JWKS_CACHE = {}
        for key_dict in jwks_data.get("keys", []):
            k_id = key_dict.get("kid")
            if k_id:
                # Convert JWK to cryptography public key object
                pub_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_dict)
                JWKS_CACHE[k_id] = pub_key

        JWKS_CACHE_EXPIRY = now + CACHE_TTL
        print(f"[RESOURCE:5004] Successfully cached {len(JWKS_CACHE)} key(s) from JWKS")

    except requests.exceptions.RequestException as e:
        print(f"[RESOURCE:5004] ERROR: Failed to fetch JWKS from IDP: {e}")
        # If cache expired but has the key, use stale cache as fallback
        if kid in JWKS_CACHE:
            return JWKS_CACHE[kid]
        return None

    return JWKS_CACHE.get(kid)


def require_token(required_scope=None):
    """
    Decorator / Middleware to validate the JWT Bearer token in the Authorization header.
    Validates:
      1. Authorization header format ('Bearer <token>')
      2. RSA-256 signature against IDP's public JWKS key
      3. Token expiration (exp claim)
      4. Issuer (iss claim matches IDP)
      5. Audience (aud claim matches resource_server)
      6. Required OAuth2 scope (if specified)
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                print("[RESOURCE:5004] Request rejected: Missing Authorization header")
                return jsonify({
                    "error": "unauthorized",
                    "error_description": "Authorization header is required (Format: Bearer <token>)"
                }), 401

            parts = auth_header.split(" ")
            if len(parts) != 2 or parts[0].lower() != "bearer":
                print("[RESOURCE:5004] Request rejected: Invalid Authorization header format")
                return jsonify({
                    "error": "invalid_request",
                    "error_description": "Authorization header must follow 'Bearer <token>' format"
                }), 401

            token = parts[1].strip()

            # 1. Read header without verification to find kid
            try:
                unverified_headers = jwt.get_unverified_header(token)
            except Exception as e:
                print(f"[RESOURCE:5004] Request rejected: Unable to parse token headers: {e}")
                return jsonify({
                    "error": "invalid_token",
                    "error_description": f"Malformed token: {str(e)}"
                }), 401

            kid = unverified_headers.get("kid")
            alg = unverified_headers.get("alg")

            if alg != "RS256":
                print(f"[RESOURCE:5004] Request rejected: Unsupported algorithm '{alg}'")
                return jsonify({
                    "error": "invalid_token",
                    "error_description": f"Algorithm '{alg}' is not accepted. Only RS256 is supported."
                }), 401

            if not kid:
                return jsonify({
                    "error": "invalid_token",
                    "error_description": "Token header is missing 'kid' (Key ID)"
                }), 401

            # 2. Get public key for this kid from JWKS
            public_key = get_signing_key(kid)
            if not public_key:
                print(f"[RESOURCE:5004] Request rejected: Public key with kid='{kid}' not found in JWKS")
                return jsonify({
                    "error": "invalid_token",
                    "error_description": f"Unknown key id '{kid}'"
                }), 401

            # 3. Cryptographically verify signature and claims
            try:
                decoded_payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    issuer=EXPECTED_ISSUER,
                    audience=EXPECTED_AUDIENCE,
                    options={"verify_exp": True, "verify_iss": True, "verify_aud": True}
                )
            except jwt.ExpiredSignatureError:
                print("[RESOURCE:5004] Request rejected: Token has EXPIRED")
                return jsonify({
                    "error": "token_expired",
                    "error_description": "The access token has expired. Please refresh your token at the IDP."
                }), 401
            except jwt.InvalidIssuerError:
                print("[RESOURCE:5004] Request rejected: Invalid issuer")
                return jsonify({
                    "error": "invalid_token",
                    "error_description": "Token issuer does not match trusted Identity Provider"
                }), 401
            except jwt.InvalidAudienceError:
                print("[RESOURCE:5004] Request rejected: Invalid audience")
                return jsonify({
                    "error": "invalid_token",
                    "error_description": f"Token audience does not match '{EXPECTED_AUDIENCE}'"
                }), 401
            except jwt.InvalidTokenError as e:
                print(f"[RESOURCE:5004] Request rejected: Signature verification failed: {e}")
                return jsonify({
                    "error": "invalid_token",
                    "error_description": f"Token verification failed: {str(e)}"
                }), 401

            # 4. Enforce Scope (if required)
            if required_scope:
                token_scopes = decoded_payload.get("scope", "").split()
                if required_scope not in token_scopes:
                    print(f"[RESOURCE:5004] Access forbidden: Missing required scope '{required_scope}'")
                    return jsonify({
                        "error": "insufficient_scope",
                        "error_description": f"Access requires scope '{required_scope}'. Granted scopes: {token_scopes}"
                    }), 403

            # Attach authenticated user payload to request
            request.current_user = decoded_payload
            print(f"[RESOURCE:5004] Token verified! Subject: '{decoded_payload.get('sub')}', Scopes: '{decoded_payload.get('scope')}'")
            return f(*args, **kwargs)

        return wrapper
    return decorator


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Information endpoint for the Resource Server."""
    return jsonify({
        "service": "Protected Resource Server (API)",
        "port": 5004,
        "status": "online",
        "authentication_method": "OAuth 2.0 Bearer JWT (RS256)",
        "trusted_idp": IDP_BASE_URL,
        "endpoints": {
            "profile": "/api/profile",
            "data": "/api/data",
            "health": "/api/health"
        }
    })


@app.route("/api/health", methods=["GET"])
def health():
    """Public health check endpoint."""
    return jsonify({"status": "healthy", "server_time": int(time.time())})


@app.route("/api/profile", methods=["GET"])
@require_token(required_scope="profile")
def get_profile():
    """
    Returns user profile details verified from the access token claims.
    Requires 'profile' scope.
    """
    user = request.current_user
    print(f"[RESOURCE:5004] GET /api/profile served for user='{user.get('sub')}'")
    return jsonify({
        "status": "success",
        "user": {
            "username": user.get("sub"),
            "email": user.get("email"),
            "name": user.get("name"),
            "user_id": user.get("user_id"),
            "scope": user.get("scope"),
            "scopes_list": user.get("scope", "").split(),
            "token_issued_at": user.get("iat"),
            "token_expires_at": user.get("exp"),
            "issuer": user.get("iss"),
            "audience": user.get("aud")
        },
        "server": "Resource Server (Port 5004)"
    })


@app.route("/api/data", methods=["GET"])
@require_token(required_scope="read")
def get_data():
    """
    Returns private documents belonging to the authenticated user.
    Requires 'read' scope.
    """
    username = request.current_user.get("sub")
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, content, category, created_at FROM user_documents WHERE username = ? ORDER BY id DESC",
        (username,)
    ).fetchall()
    conn.close()

    documents = [dict(row) for row in rows]
    print(f"[RESOURCE:5004] GET /api/data returning {len(documents)} document(s) for user='{username}'")

    return jsonify({
        "status": "success",
        "username": username,
        "count": len(documents),
        "documents": documents
    })


@app.route("/api/data", methods=["POST"])
@require_token(required_scope="write")
def create_data():
    """
    Creates a new private document for the authenticated user.
    Requires 'write' scope.
    """
    username = request.current_user.get("sub")
    body = request.get_json(silent=True) or request.form.to_dict()

    title = (body.get("title") or "").strip()
    content = (body.get("content") or "").strip()
    category = (body.get("category") or "General").strip()

    if not title or not content:
        return jsonify({
            "error": "invalid_request",
            "error_description": "title and content are required fields"
        }), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_documents (username, title, content, category) VALUES (?, ?, ?, ?)",
        (username, title, content, category)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()

    print(f"[RESOURCE:5004] POST /api/data: Created document id={doc_id} ('{title}') for user='{username}'")

    return jsonify({
        "status": "success",
        "message": "Document created successfully",
        "document": {
            "id": doc_id,
            "username": username,
            "title": title,
            "content": content,
            "category": category
        }
    }), 201


# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("      RESOURCE SERVER (PROTECTED API) STARTING ON PORT 5004     ")
    print("=" * 65)
    print(f" * Base URL:            http://localhost:5004")
    print(f" * Profile Endpoint:    http://localhost:5004/api/profile (Scope: profile)")
    print(f" * Data List Endpoint:  http://localhost:5004/api/data    (Scope: read)")
    print(f" * Data Create Endpoint:http://localhost:5004/api/data    (Scope: write)")
    print(f" * Trusted IDP JWKS:    {JWKS_URL}")
    print(f" * Token Validation:    RS256 via IDP Public Key Set")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5004, debug=False)
