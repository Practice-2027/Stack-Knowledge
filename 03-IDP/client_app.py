"""
client_app.py
=============
Client Web Application demonstrating OAuth 2.0 & OpenID Connect consumption.
Runs on Port 5005.

Core Responsibilities:
1. Initiates the OAuth 2.0 Authorization Code flow with the IDP (Port 5003).
2. Handles the OAuth 2.0 redirect callback and securely exchanges the authorization code for tokens.
3. Stores tokens securely in server-side session cookies.
4. Uses Bearer Access Tokens to access the Protected Resource Server (Port 5004).
5. Automatically handles Access Token expiration using Refresh Tokens.
6. Provides an educational JWT Inspector showing how tokens are structured.
"""

import os
import sys
import time
import json
import secrets
from datetime import datetime, timezone
import requests
from flask import Flask, request, session, redirect, url_for, render_template, jsonify
import jwt

# ---------------------------------------------------------
# Flask App Configuration
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.config["SECRET_KEY"] = secrets.token_hex(32)

# Server URLs and OAuth Client Credentials
IDP_BASE_URL = os.environ.get("IDP_BASE_URL", "http://localhost:5003")
RESOURCE_SERVER_URL = os.environ.get("RESOURCE_SERVER_URL", "http://localhost:5004")

CLIENT_ID = "client_app_demo"
CLIENT_SECRET = "super-secret-client-password"
REDIRECT_URI = "http://localhost:5005/callback"
REQUESTED_SCOPES = "openid profile email read write"


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def refresh_access_token():
    """
    Attempts to exchange the current refresh token for a fresh access token.
    Returns True if refreshed successfully, False otherwise.
    """
    r_token = session.get("refresh_token")
    if not r_token:
        print("[CLIENT:5005] Cannot refresh: No refresh token in session")
        return False

    print("[CLIENT:5005] Attempting back-channel token refresh with IDP...")
    try:
        resp = requests.post(
            f"{IDP_BASE_URL}/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": r_token,
                "client_id": CLIENT_ID
            },
            timeout=5
        )
        if resp.status_code == 200:
            token_data = resp.json()
            session["access_token"] = token_data.get("access_token")
            # If a new refresh token is issued, update it too
            if "refresh_token" in token_data:
                session["refresh_token"] = token_data["refresh_token"]
            print("[CLIENT:5005] Access token refreshed successfully via refresh token!")
            return True
        else:
            print(f"[CLIENT:5005] Token refresh failed with status {resp.status_code}: {resp.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[CLIENT:5005] Token refresh network error: {e}")
        return False


def make_authenticated_api_request(method, url, json_data=None):
    """
    Makes an HTTP request to the Resource Server with the current access token.
    If the access token has expired (HTTP 401), attempts to automatically refresh
    the token and retries the request once.
    """
    token = session.get("access_token")
    if not token:
        return None, "Not authenticated"

    headers = {"Authorization": f"Bearer {token}"}
    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, timeout=5)
        else:
            resp = requests.post(url, headers=headers, json=json_data, timeout=5)

        # Handle token expiration (HTTP 401)
        if resp.status_code == 401:
            print("[CLIENT:5005] Resource server returned 401. Trying automatic token refresh...")
            refreshed = refresh_access_token()
            if refreshed:
                # Retry with new token
                new_token = session.get("access_token")
                headers = {"Authorization": f"Bearer {new_token}"}
                if method.upper() == "GET":
                    resp = requests.get(url, headers=headers, timeout=5)
                else:
                    resp = requests.post(url, headers=headers, json=json_data, timeout=5)

        return resp, None
    except requests.exceptions.RequestException as e:
        return None, f"Network error contacting resource server: {str(e)}"


# ---------------------------------------------------------
# Web Routes
# ---------------------------------------------------------

@app.route("/")
def home():
    """Client App Home Page."""
    message = request.args.get("message")
    return render_template("home.html", message=message)


@app.route("/login")
def login():
    """
    OAuth 2.0 Login Initiation.
    Generates a cryptographically random 'state' string for CSRF protection,
    stores it in the session, and redirects user to the IDP Authorization endpoint.
    """
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state

    # Build standard OAuth2 authorization URL
    auth_url = (
        f"{IDP_BASE_URL}/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={requests.utils.quote(REQUESTED_SCOPES)}"
        f"&state={state}"
    )

    print(f"[CLIENT:5005] Initiating OAuth login -> Redirecting to IDP: {auth_url}")
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """
    OAuth 2.0 Redirect Callback Endpoint.
    1. Verifies the 'state' parameter to prevent CSRF attacks.
    2. Receives the temporary authorization 'code'.
    3. Makes a secure server-to-server POST request to IDP's /token endpoint
       exchanging the code for access_token, refresh_token, and id_token.
    4. Stores tokens and user profile in the session.
    """
    received_code = request.args.get("code")
    received_state = request.args.get("state")
    error = request.args.get("error")

    if error:
        print(f"[CLIENT:5005] IDP returned OAuth error: {error}")
        return redirect(url_for("home", message=f"OAuth Authorization Error: {error}"))

    # CSRF Check: Validate state parameter
    expected_state = session.get("oauth_state")
    if not received_state or received_state != expected_state:
        print(f"[CLIENT:5005] State validation failed! Received='{received_state}', Expected='{expected_state}'")
        return redirect(url_for("home", message="Security Error: State parameter mismatch (CSRF suspected)"))

    if not received_code:
        return redirect(url_for("home", message="Error: No authorization code received from IDP"))

    print(f"[CLIENT:5005] Received auth code: '{received_code[:12]}...'. Exchanging for tokens at IDP...")

    # Back-channel token exchange
    try:
        token_response = requests.post(
            f"{IDP_BASE_URL}/token",
            data={
                "grant_type": "authorization_code",
                "code": received_code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI
            },
            timeout=5
        )

        if token_response.status_code != 200:
            print(f"[CLIENT:5005] Token exchange failed ({token_response.status_code}): {token_response.text}")
            return redirect(url_for("home", message="Failed to exchange authorization code for tokens"))

        tokens = token_response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        id_token = tokens.get("id_token")

        # Decode token payload without signature verification on the client side
        # (Resource Server will verify signature independently with JWKS)
        decoded_payload = jwt.decode(access_token, options={"verify_signature": False})

        # Store in session
        session["access_token"] = access_token
        session["refresh_token"] = refresh_token
        session["id_token"] = id_token
        session["user"] = {
            "username": decoded_payload.get("sub"),
            "email": decoded_payload.get("email"),
            "name": decoded_payload.get("name")
        }

        print(f"[CLIENT:5005] Successfully logged in user: @{decoded_payload.get('sub')}")
        return redirect(url_for("profile", message="Login successful via OAuth 2.0!"))

    except requests.exceptions.RequestException as e:
        print(f"[CLIENT:5005] Error during token exchange: {e}")
        return redirect(url_for("home", message=f"Network error during token exchange: {str(e)}"))


@app.route("/profile")
def profile():
    """
    Profile page.
    Queries the Protected Resource Server (Port 5004) for user profile data using
    the Bearer Access Token, and breaks down the JWT for educational inspection.
    """
    if "access_token" not in session:
        return redirect(url_for("home", message="Please sign in to view your profile"))

    resp, err = make_authenticated_api_request("GET", f"{RESOURCE_SERVER_URL}/api/profile")

    if err or not resp or resp.status_code != 200:
        error_msg = err or (resp.json().get("error_description") if resp else "Failed to fetch profile")
        return render_template(
            "profile.html",
            error=f"Error contacting Resource Server: {error_msg}",
            user=session.get("user", {}),
            raw_token_header="", raw_token_payload="", raw_token_sig="",
            decoded_header_json="{}", decoded_payload_json="{}"
        )

    profile_data = resp.json().get("user", {})

    # Split JWT for visualizer (header.payload.signature)
    token = session["access_token"]
    parts = token.split(".")
    raw_header = parts[0] if len(parts) > 0 else ""
    raw_payload = parts[1] if len(parts) > 1 else ""
    raw_sig = parts[2] if len(parts) > 2 else ""

    # Decode header and payload JSON
    try:
        decoded_header = jwt.get_unverified_header(token)
        decoded_header_json = json.dumps(decoded_header, indent=2)
    except Exception:
        decoded_header_json = "{}"

    try:
        decoded_payload = jwt.decode(token, options={"verify_signature": False})
        decoded_payload_json = json.dumps(decoded_payload, indent=2)
    except Exception:
        decoded_payload_json = "{}"

    # Format expiration timestamp
    exp_ts = decoded_payload.get("exp", 0)
    expires_readable = datetime.fromtimestamp(exp_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return render_template(
        "profile.html",
        user=profile_data,
        raw_token_header=raw_header,
        raw_token_payload=raw_payload,
        raw_token_sig=raw_sig,
        decoded_header_json=decoded_header_json,
        decoded_payload_json=decoded_payload_json,
        expires_readable=expires_readable,
        message=request.args.get("message")
    )


@app.route("/data", methods=["GET", "POST"])
def data():
    """
    Protected Data page.
    GET: Queries Resource Server GET /api/data with Bearer token.
    POST: Sends new confidential document to Resource Server POST /api/data with Bearer token.
    """
    if "access_token" not in session:
        return redirect(url_for("home", message="Please sign in to view protected data"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category = request.form.get("category", "General")

        resp, err = make_authenticated_api_request(
            "POST",
            f"{RESOURCE_SERVER_URL}/api/data",
            json_data={"title": title, "content": content, "category": category}
        )

        if err or not resp or resp.status_code not in (200, 201):
            error_desc = err or (resp.json().get("error_description") if resp else "Failed to save document")
            return redirect(url_for("data", error=f"Could not save document: {error_desc}"))

        return redirect(url_for("data", message="Document saved securely to Resource Server!"))

    # GET request
    resp, err = make_authenticated_api_request("GET", f"{RESOURCE_SERVER_URL}/api/data")
    if err or not resp or resp.status_code != 200:
        error_desc = err or (resp.json().get("error_description") if resp else "Failed to fetch data")
        return render_template(
            "data.html",
            error=f"Resource Server Error: {error_desc}",
            documents=[],
            username=session.get("user", {}).get("username", "user")
        )

    data_json = resp.json()
    documents = data_json.get("documents", [])
    username = data_json.get("username", session.get("user", {}).get("username", "user"))

    return render_template(
        "data.html",
        documents=documents,
        username=username,
        message=request.args.get("message"),
        error=request.args.get("error")
    )


@app.route("/refresh-token")
def manual_refresh():
    """Manual endpoint for testing the OAuth 2.0 refresh token grant."""
    if "refresh_token" not in session:
        return redirect(url_for("home", message="No active session to refresh"))

    success = refresh_access_token()
    if success:
        return redirect(url_for("profile", message="Access token refreshed successfully via Refresh Token grant!"))
    else:
        return redirect(url_for("home", message="Failed to refresh token. Session may have expired."))


@app.route("/logout")
def logout():
    """Clears local session cookies."""
    user = session.get("user", {}).get("username", "User")
    session.clear()
    print(f"[CLIENT:5005] User '{user}' logged out. Session cleared.")
    return redirect(url_for("home", message="You have been logged out successfully."))


# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("        OAUTH CLIENT APPLICATION STARTING ON PORT 5005         ")
    print("=" * 65)
    print(" * Application URL:     http://localhost:5005")
    print(" * Configured IDP:      http://localhost:5003")
    print(" * Resource Server:     http://localhost:5004")
    print(" * Client ID:           client_app_demo")
    print(" * Callback Redirect:   http://localhost:5005/callback")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5005, debug=False)
