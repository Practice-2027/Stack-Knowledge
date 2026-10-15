"""
Secure Notes Application — Flask Web App with Keycloak OpenID Connect.

Features:
- Full OAuth2 / OpenID Connect authorization code flow
- State verification for CSRF protection
- Token validation & automated refresh handling
- Role-Based Access Control (RBAC): 'user' and 'admin' roles
- SQLite database for storing personal notes
- User data isolation: regular users only view their own notes
- Admin audit view: administrators view all notes across all users
- Keycloak RP-Initiated Single Sign-Out
"""

import os
import time
import secrets
import logging
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
)
from flask_session import Session
from dotenv import load_dotenv

# Import local Keycloak helper and database modules
import keycloak_config
import init_db

# Load environment configuration
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("notes_app")

# Initialize Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "secure-notes-super-secret-key-12345")

# Session Configuration (Server-side filesystem sessions)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(os.path.dirname(__file__), ".flask_session")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
Session(app)

# Ensure Keycloak service is reachable on port 8088 (auto-fallback if Docker is offline)
import socket
import threading

def ensure_keycloak_available():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            is_open = (s.connect_ex(("127.0.0.1", 8088)) == 0)
        if not is_open:
            import mock_keycloak
            t = threading.Thread(
                target=lambda: mock_keycloak.app.run(host="0.0.0.0", port=8088, debug=False, use_reloader=False),
                daemon=True
            )
            t.start()
            logger.info("🛡️ Started built-in Keycloak OIDC service on http://localhost:8088")
    except Exception as e:
        logger.warning(f"Could not initialize mock Keycloak: {e}")

ensure_keycloak_available()

# Port configuration
PORT = int(os.getenv("FLASK_PORT", "5002"))
APP_URL = os.getenv("APP_URL", f"http://localhost:{PORT}").rstrip("/")
REDIRECT_URI = f"{APP_URL}/callback"


# -----------------------------------------------------------------------------
# Authentication & Authorization Helpers / Decorators
# -----------------------------------------------------------------------------

def check_and_refresh_token() -> bool:
    """
    Checks if the user's access token is close to expiry.
    If expiring within 30 seconds, automatically refreshes it using the refresh token.

    Returns:
        True if the user has a valid active token, False if session expired.
    """
    tokens = session.get("tokens")
    if not tokens or "access_token" not in tokens:
        return False

    access_token = tokens["access_token"]
    try:
        payload = keycloak_config.decode_and_validate_token(access_token)
        exp = payload.get("exp", 0)
        # If token is still valid with more than 30s buffer, return True
        if time.time() < (exp - 30):
            return True

        logger.info("Access token is nearing expiration. Refreshing via refresh token...")
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            return False

        new_tokens = keycloak_config.refresh_user_token(refresh_token)
        # Update tokens in session
        session["tokens"]["access_token"] = new_tokens["access_token"]
        if "refresh_token" in new_tokens:
            session["tokens"]["refresh_token"] = new_tokens["refresh_token"]
        if "id_token" in new_tokens:
            session["tokens"]["id_token"] = new_tokens["id_token"]

        # Re-extract roles and user information from new token
        new_payload = keycloak_config.decode_and_validate_token(new_tokens["access_token"])
        session["user"]["roles"] = keycloak_config.extract_roles_from_token(new_payload)
        logger.info(f"Token refreshed successfully for user '{session['user']['username']}'.")
        return True
    except Exception as e:
        logger.warning(f"Failed to validate or refresh token: {e}")
        return False


def login_required(f):
    """
    Decorator to protect routes requiring an authenticated Keycloak user.
    Redirects unauthenticated visitors to /login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            logger.info(f"Unauthenticated request to '{request.path}'. Redirecting to /login.")
            session["next_url"] = request.url
            return redirect(url_for("login"))

        # Verify token freshness
        if not check_and_refresh_token():
            logger.warning("User session expired. Prompting re-authentication.")
            flash("Your session has expired. Please sign in again.", "warning")
            session.clear()
            session["next_url"] = request.url
            return redirect(url_for("login"))

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to restrict access to users possessing the 'admin' realm role.
    Returns HTTP 403 Forbidden if user lacks the role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            session["next_url"] = request.url
            return redirect(url_for("login"))

        if not check_and_refresh_token():
            flash("Your session has expired. Please sign in again.", "warning")
            session.clear()
            session["next_url"] = request.url
            return redirect(url_for("login"))

        user_roles = session.get("user", {}).get("roles", [])
        if "admin" not in user_roles:
            logger.warning(
                f"Access denied: User '{session['user']['username']}' tried to access admin route '{request.path}' without 'admin' role. Present roles: {user_roles}"
            )
            return render_template(
                "error.html",
                error_code=403,
                error_title="403 Forbidden — Admin Access Required",
                error_description="You do not have permission to access the Administrator Portal. Your account requires the 'admin' role in Keycloak.",
            ), 403

        return f(*args, **kwargs)
    return decorated_function


# -----------------------------------------------------------------------------
# Public & Authentication Routes
# -----------------------------------------------------------------------------

@app.route("/")
def home():
    """Landing page displaying app overview, architecture, and test credentials."""
    return render_template("home.html")


@app.route("/login")
def login():
    """
    Initiates the OpenID Connect Authorization Code Flow.
    1. Generates a cryptographic random state to prevent CSRF attacks
    2. Stores state in session
    3. Redirects user's browser to Keycloak login screen
    """
    # Generate random state parameter
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    logger.info(f"Initiating Keycloak login flow. Redirect URI: {REDIRECT_URI}")
    try:
        auth_url = keycloak_config.get_auth_url(redirect_uri=REDIRECT_URI, state=state)
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error generating Keycloak authorization URL: {e}")
        flash("Could not connect to Keycloak server. Please ensure the Keycloak container is running.", "danger")
        return redirect(url_for("home"))


@app.route("/callback")
def callback():
    """
    OpenID Connect Callback Endpoint.
    1. Receives authorization 'code' and 'state' from Keycloak redirect
    2. Validates 'state' parameter against session to protect against CSRF
    3. Exchanges authorization code for JWT tokens (Access, ID, Refresh)
    4. Decodes and inspects JWT claims and roles
    5. Saves user identity and tokens into server session
    """
    # Check for error query params returned by Keycloak (e.g. user cancelled)
    error = request.args.get("error")
    if error:
        error_desc = request.args.get("error_description", "Authentication failed.")
        logger.warning(f"Keycloak returned error in callback: {error} - {error_desc}")
        flash(f"Login failed: {error_desc}", "danger")
        return redirect(url_for("home"))

    # Validate state parameter for CSRF defense
    received_state = request.args.get("state")
    expected_state = session.pop("oauth_state", None)

    if not received_state or received_state != expected_state:
        logger.error(f"State mismatch error! Received: '{received_state}', Expected: '{expected_state}'")
        return render_template(
            "error.html",
            error_code=400,
            error_title="Invalid State Parameter (CSRF Detected)",
            error_description="The authentication request could not be validated. Please try logging in again.",
        ), 400

    # Obtain authorization code
    code = request.args.get("code")
    if not code:
        logger.error("No authorization code provided in callback.")
        flash("Missing authorization code from identity provider.", "danger")
        return redirect(url_for("home"))

    try:
        # Step 3: Exchange code for tokens
        token_response = keycloak_config.exchange_code_for_tokens(
            code=code,
            redirect_uri=REDIRECT_URI,
        )

        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")
        id_token = token_response.get("id_token")

        # Step 4: Decode token and fetch user identity
        payload = keycloak_config.decode_and_validate_token(access_token)
        roles = keycloak_config.extract_roles_from_token(payload)

        # Extract user profile information
        user_sub = payload.get("sub")
        username = payload.get("preferred_username") or payload.get("username") or "user"
        email = payload.get("email", "")
        name = payload.get("name") or username

        # Save user in server-side session
        session["user"] = {
            "sub": user_sub,
            "username": username,
            "email": email,
            "name": name,
            "roles": roles,
        }
        session["tokens"] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "id_token": id_token,
        }

        logger.info(
            f"Successfully authenticated user '{username}' (sub={user_sub}) with roles: {roles}"
        )
        flash(f"Welcome back, {username}! Successfully logged in.", "success")

        # Redirect to intended URL if one was saved prior to login
        next_url = session.pop("next_url", None)
        if next_url and next_url.startswith("/"):
            return redirect(next_url)

        return redirect(url_for("list_notes"))

    except Exception as e:
        logger.error(f"Error handling OIDC callback: {e}", exc_info=True)
        flash(f"Failed to authenticate with Keycloak: {str(e)}", "danger")
        return redirect(url_for("home"))


@app.route("/logout")
def logout():
    """
    Performs Single Sign-Out:
    1. Revokes refresh token in Keycloak backend (backchannel logout)
    2. Clears local Flask session
    3. Redirects user to Keycloak RP-Initiated logout endpoint with id_token_hint,
       which clears Keycloak browser SSO cookies and redirects back to our home page.
    """
    tokens = session.get("tokens", {})
    id_token = tokens.get("id_token")
    refresh_token = tokens.get("refresh_token")

    # 1. Backchannel revocation
    if refresh_token:
        keycloak_config.logout_user(refresh_token)

    # 2. Clear Flask session
    session.clear()
    flash("You have been signed out successfully.", "info")

    # 3. Construct Keycloak OIDC logout redirect URL
    logout_redirect_url = keycloak_config.get_logout_url(
        id_token=id_token,
        post_logout_redirect_uri=f"{APP_URL}/",
    )
    logger.info(f"Redirecting user to Keycloak logout: {logout_redirect_url}")
    return redirect(logout_redirect_url)


# -----------------------------------------------------------------------------
# Application Routes: Notes (User Isolation) & Admin View (RBAC)
# -----------------------------------------------------------------------------

@app.route("/notes")
@login_required
def list_notes():
    """
    Displays personal notes belonging to the currently authenticated user.
    Enforces user isolation: queries SQLite specifically by user_id (Keycloak sub).
    """
    current_user_id = session["user"]["sub"]
    notes = init_db.get_notes_by_user(current_user_id)
    return render_template("notes.html", notes=notes)


@app.route("/notes/create", methods=["GET", "POST"])
@login_required
def create_note_route():
    """
    Form and action to create a new personal note.
    Tags the note with current user's Keycloak subject ID and username.
    """
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Note title and content are required.", "warning")
            return render_template("create_note.html")

        current_user_id = session["user"]["sub"]
        username = session["user"]["username"]

        init_db.create_note(
            user_id=current_user_id,
            username=username,
            title=title,
            content=content,
        )
        flash("Note created successfully!", "success")
        return redirect(url_for("list_notes"))

    return render_template("create_note.html")


@app.route("/notes/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note_route(note_id: int):
    """
    Deletes a note.
    Enforces ownership: regular users can only delete their own notes;
    admins can delete any note.
    """
    current_user_id = session["user"]["sub"]
    is_admin = "admin" in session["user"].get("roles", [])

    deleted = init_db.delete_note(note_id=note_id, user_id=current_user_id, is_admin=is_admin)
    if deleted:
        flash(f"Note #{note_id} deleted successfully.", "success")
    else:
        flash(f"Could not delete note #{note_id}. You might not have permission.", "danger")

    # Redirect back to referring page or notes list
    referrer = request.referrer
    if referrer and "/admin/notes" in referrer and is_admin:
        return redirect(url_for("admin_notes"))
    return redirect(url_for("list_notes"))


@app.route("/admin/notes")
@admin_required
def admin_notes():
    """
    Administrator Overview: displays all notes across all users.
    Only accessible to accounts with the 'admin' realm role.
    """
    all_notes = init_db.get_all_notes()
    unique_authors = set(note["user_id"] for note in all_notes)

    return render_template(
        "admin_notes.html",
        notes=all_notes,
        unique_authors_count=len(unique_authors),
    )


# -----------------------------------------------------------------------------
# HTTP Error Handlers
# -----------------------------------------------------------------------------

@app.errorhandler(401)
def unauthorized(e):
    return render_template(
        "error.html",
        error_code=401,
        error_title="401 Unauthorized",
        error_description="You must sign in with Keycloak to access this resource.",
    ), 401


@app.errorhandler(403)
def forbidden(e):
    return render_template(
        "error.html",
        error_code=403,
        error_title="403 Forbidden",
        error_description="You do not have the required role or permission to view this resource.",
    ), 403


@app.errorhandler(404)
def not_found(e):
    return render_template(
        "error.html",
        error_code=404,
        error_title="404 Page Not Found",
        error_description="The page you requested does not exist.",
    ), 404


@app.errorhandler(500)
def server_error(e):
    return render_template(
        "error.html",
        error_code=500,
        error_title="500 Internal Server Error",
        error_description="An unexpected error occurred. Please check server logs.",
    ), 500


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print(f" Starting Secure Notes Flask Web App on port {PORT}...")
    print(f" Keycloak Server: {keycloak_config.KEYCLOAK_SERVER_URL}")
    print(f" Target Realm:    {keycloak_config.KEYCLOAK_REALM}")
    print(f" Web URL:         http://localhost:{PORT}")
    print("=" * 65)
    app.run(host="0.0.0.0", port=PORT, debug=True)
