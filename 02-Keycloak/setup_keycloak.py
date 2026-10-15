"""
Automated Keycloak Setup Script for Secure Notes Application.

This script connects to the running Keycloak instance, waits for it to finish
starting up (with retry logic), and automatically configures:
1. Realm: 'notes-app'
2. Client: 'notes-client' (Confidential client with redirect URIs and secret)
3. Realm Roles: 'user' and 'admin'
4. Test Users:
   - 'testuser' (password: 'password') with 'user' role
   - 'admin' (password: 'password') with 'admin' and 'user' roles

Can be executed repeatedly without errors (idempotent).
"""

import os
import sys
import time
import logging
import requests
from dotenv import load_dotenv
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Load environment configuration
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("setup_keycloak")

# Configuration from environment with robust defaults
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/").rstrip("/") + "/"
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
TARGET_REALM = os.getenv("KEYCLOAK_REALM", "notes-app")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "notes-client")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "notes-client-secret")
APP_PORT = int(os.getenv("FLASK_PORT", "5002"))


def wait_for_keycloak(max_retries: int = 35, delay_seconds: int = 3) -> bool:
    """
    Polls the Keycloak server until it is online and ready to accept connections.
    Quarkus Keycloak typically takes 15-40 seconds to complete initialization.

    Args:
        max_retries: Maximum number of polling attempts
        delay_seconds: Seconds between attempts

    Returns:
        True when server is responsive, False if timeout exceeded.
    """
    health_url = f"{KEYCLOAK_SERVER_URL}realms/master"
    logger.info(f"Checking Keycloak availability at {health_url}...")

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(health_url, timeout=3)
            if resp.status_code == 200:
                logger.info(f"[OK] Keycloak is UP and healthy! (attempt {attempt}/{max_retries})")
                return True
            else:
                logger.info(f"Attempt {attempt}/{max_retries}: Server responded with status {resp.status_code}. Waiting {delay_seconds}s...")
        except requests.exceptions.RequestException:
            logger.info(f"Attempt {attempt}/{max_retries}: Keycloak is still starting up... Waiting {delay_seconds}s...")

        time.sleep(delay_seconds)

    logger.error("Timed out waiting for Keycloak to start up.")
    return False


def setup_keycloak():
    """Main orchestration function to set up realm, client, roles, and test users."""
    print("=" * 65)
    print("  KEYCLOAK AUTOMATED CONFIGURATION FOR SECURE NOTES APP  ")
    print("=" * 65)

    # 1. Wait for server readiness
    if not wait_for_keycloak():
        print("\n[ERROR] Keycloak server is not reachable at http://localhost:8080/.")
        print("Please ensure Docker Compose is running:")
        print("    docker compose up -d\n")
        sys.exit(1)

    # 2. Authenticate as Master Administrator
    logger.info(f"Connecting to Keycloak Admin API as '{KEYCLOAK_ADMIN_USER}'...")
    try:
        admin = KeycloakAdmin(
            server_url=KEYCLOAK_SERVER_URL,
            username=KEYCLOAK_ADMIN_USER,
            password=KEYCLOAK_ADMIN_PASSWORD,
            realm_name="master",
            verify=True,
        )
        logger.info("Successfully authenticated with Keycloak Master Realm.")
    except Exception as e:
        logger.error(f"Failed to authenticate with Keycloak: {e}")
        print("\n[ERROR] Could not log into Keycloak with admin credentials.")
        print("Verify KEYCLOAK_ADMIN and KEYCLOAK_ADMIN_PASSWORD in docker-compose.yml / .env.")
        sys.exit(1)

    # 3. Create Realm: notes-app
    logger.info(f"Checking if realm '{TARGET_REALM}' exists...")
    existing_realms = [r["realm"] for r in admin.get_realms()]

    realm_payload = {
        "realm": TARGET_REALM,
        "displayName": "Secure Notes Realm",
        "enabled": True,
        "registrationAllowed": True,       # Allow self-registration from Keycloak login page
        "rememberMe": True,                # Support remember me checkbox
        "resetPasswordAllowed": True,      # Enable self-service password reset
        "loginWithEmailAllowed": True,     # Allow login with either username or email
        "duplicateEmailsAllowed": False,
        "sslRequired": "external",         # Relaxed SSL for local development
    }

    if TARGET_REALM not in existing_realms:
        logger.info(f"Creating new realm: '{TARGET_REALM}'...")
        admin.create_realm(payload=realm_payload, skip_exists=True)
        logger.info(f"[OK] Realm '{TARGET_REALM}' created.")
    else:
        logger.info(f"Realm '{TARGET_REALM}' already exists.")

    # Switch admin context to target realm
    admin.realm_name = TARGET_REALM

    # 4. Create or Update Client: notes-client
    logger.info(f"Configuring client '{CLIENT_ID}' in realm '{TARGET_REALM}'...")
    redirect_uris = [
        f"http://localhost:{APP_PORT}/*",
        f"http://127.0.0.1:{APP_PORT}/*",
        f"http://localhost:{APP_PORT}/callback",
        f"http://127.0.0.1:{APP_PORT}/callback",
    ]
    post_logout_redirect_uris = f"http://localhost:{APP_PORT}/*##http://127.0.0.1:{APP_PORT}/*"

    client_payload = {
        "clientId": CLIENT_ID,
        "name": "Secure Notes Web Application",
        "description": "Client for Flask OIDC Authentication",
        "enabled": True,
        "publicClient": False,                 # Confidential client requiring client secret
        "clientAuthenticatorType": "client-secret",
        "secret": CLIENT_SECRET,
        "standardFlowEnabled": True,           # Enable OAuth2 Authorization Code Grant Flow
        "directAccessGrantsEnabled": True,     # Enable Resource Owner Password Grant
        "serviceAccountsEnabled": False,
        "redirectUris": redirect_uris,
        "webOrigins": ["*"],
        "attributes": {
            "post.logout.redirect.uris": post_logout_redirect_uris,
            "pkce.code.challenge.method": "S256",
        },
    }

    client_internal_id = admin.get_client_id(CLIENT_ID)
    if not client_internal_id:
        logger.info(f"Creating confidential client '{CLIENT_ID}'...")
        admin.create_client(payload=client_payload, skip_exists=True)
        client_internal_id = admin.get_client_id(CLIENT_ID)
        logger.info(f"[OK] Client '{CLIENT_ID}' created with internal ID: {client_internal_id}")
    else:
        logger.info(f"Client '{CLIENT_ID}' already exists (ID: {client_internal_id}). Updating configuration...")
        admin.update_client(client_id=client_internal_id, payload=client_payload)
        logger.info(f"[OK] Client '{CLIENT_ID}' updated.")

    # 5. Create Realm Roles: user, admin
    roles_to_create = [
        {"name": "user", "description": "Standard user - can create and view personal notes"},
        {"name": "admin", "description": "Administrator - can inspect all notes across all users"},
    ]

    for role_def in roles_to_create:
        role_name = role_def["name"]
        try:
            admin.create_realm_role(payload=role_def, skip_exists=True)
            logger.info(f"[OK] Realm role '{role_name}' created or confirmed.")
        except Exception as e:
            logger.info(f"Role '{role_name}' already exists or noted: {e}")

    # Fetch role representations for assignment
    user_role_rep = admin.get_realm_role(role_name="user")
    admin_role_rep = admin.get_realm_role(role_name="admin")

    # 6. Create Test Users
    test_users = [
        {
            "username": "testuser",
            "email": "testuser@example.com",
            "firstName": "Test",
            "lastName": "User",
            "password": "password",
            "roles": [user_role_rep],
        },
        {
            "username": "admin",
            "email": "admin@example.com",
            "firstName": "System",
            "lastName": "Admin",
            "password": "password",
            "roles": [admin_role_rep, user_role_rep],
        },
    ]

    for u in test_users:
        uname = u["username"]
        uid = admin.get_user_id(uname)
        if not uid:
            logger.info(f"Creating test user '{uname}'...")
            user_data = {
                "username": uname,
                "email": u["email"],
                "firstName": u["firstName"],
                "lastName": u["lastName"],
                "enabled": True,
                "emailVerified": True,
            }
            uid = admin.create_user(payload=user_data, exist_ok=True)
            logger.info(f"[OK] User '{uname}' created with UUID: {uid}")
        else:
            logger.info(f"User '{uname}' already exists (UUID: {uid}).")

        # Set permanent password (temporary=False avoids forced password reset on first login)
        admin.set_user_password(user_id=uid, password=u["password"], temporary=False)
        logger.info(f"[OK] Set permanent password for '{uname}'.")

        # Assign roles
        try:
            admin.assign_realm_roles(user_id=uid, roles=u["roles"])
            assigned_names = [r["name"] for r in u["roles"]]
            logger.info(f"[OK] Assigned roles {assigned_names} to user '{uname}'.")
        except Exception as e:
            logger.warning(f"Note assigning roles to '{uname}': {e}")

    # 7. Print summary and testing guide
    print("\n" + "=" * 65)
    print("      KEYCLOAK SETUP COMPLETED SUCCESSFULLY!      ")
    print("=" * 65)
    print(f" Realm Name:     {TARGET_REALM}")
    print(f" Client ID:      {CLIENT_ID}")
    print(f" Client Secret:  {CLIENT_SECRET}")
    print(f" Admin Console:  {KEYCLOAK_SERVER_URL}admin/")
    print("-" * 65)
    print(" CONFIGURED TEST ACCOUNTS:")
    print("   1) Regular User:")
    print("      - Username: testuser")
    print("      - Password: password")
    print("      - Roles:    ['user']")
    print("      - Can access: /notes, /notes/create")
    print("   2) Administrator:")
    print("      - Username: admin")
    print("      - Password: password")
    print("      - Roles:    ['admin', 'user']")
    print("      - Can access: /notes, /notes/create, /admin/notes")
    print("-" * 65)
    print(" NEXT STEP:")
    print(f" Run the Flask application: python app.py")
    print(f" Open your browser at:     http://localhost:{APP_PORT}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    setup_keycloak()
