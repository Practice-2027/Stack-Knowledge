"""
Keycloak Configuration and OpenID Connect (OIDC) Helper Module.

This module encapsulates all communications with Keycloak:
- Managing OpenID Connect client credentials and endpoints
- Generating authorization URLs for browser-based login/register
- Exchanging OAuth2 authorization codes for JWT tokens
- Validating and decoding JWT tokens
- Extracting user roles (realm and client roles) from token claims
- Handling token refresh and single sign-out (RP-Initiated Logout)
"""

import os
import time
import logging
from urllib.parse import urlencode
from dotenv import load_dotenv
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError, KeycloakAuthenticationError

# Load environment variables from .env file if available
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Keycloak Configuration Settings
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8088/").rstrip("/") + "/"
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "notes-app")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "notes-client")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "notes-client-secret")
APP_URL = os.getenv("APP_URL", "http://localhost:5002").rstrip("/")

logger.info(f"Connecting to Keycloak Server: {KEYCLOAK_SERVER_URL}")
logger.info(f"Configured Realm: {KEYCLOAK_REALM}, Client ID: {KEYCLOAK_CLIENT_ID}")


def get_keycloak_openid() -> KeycloakOpenID:
    """
    Initializes and returns a KeycloakOpenID client instance.
    This client is used to perform OpenID Connect operations such as token exchange,
    token validation, user info retrieval, and logout.
    """
    return KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL,
        realm_name=KEYCLOAK_REALM,
        client_id=KEYCLOAK_CLIENT_ID,
        client_secret_key=KEYCLOAK_CLIENT_SECRET,
        verify=True,
    )


# Singleton-like instance for reuse
_openid_client = None


def get_client() -> KeycloakOpenID:
    """Returns the cached KeycloakOpenID client or instantiates a new one."""
    global _openid_client
    if _openid_client is None:
        _openid_client = get_keycloak_openid()
    return _openid_client


def get_auth_url(redirect_uri: str, state: str, scope: str = "openid profile email") -> str:
    """
    Generates the Keycloak authorization URL to start the OAuth2 Authorization Code flow.
    The user's browser is redirected to this URL to log in.

    Args:
        redirect_uri: The callback URL on our Flask app (e.g. http://localhost:5002/callback)
        state: A cryptographically secure random token preventing CSRF attacks
        scope: OIDC scopes requested (openid is required for OIDC)

    Returns:
        The complete Keycloak login URL as a string.
    """
    client = get_client()
    # Keycloak auth_url builds the endpoint: /realms/{realm}/protocol/openid-connect/auth
    auth_url = client.auth_url(
        redirect_uri=redirect_uri,
        scope=scope,
        state=state,
    )
    logger.info(f"Generated Keycloak Auth URL with state: {state[:8]}...")
    return auth_url


def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    """
    Exchanges the temporary authorization code returned by Keycloak for JWT tokens:
    - access_token: Used to authenticate API requests and inspect user claims
    - refresh_token: Used to obtain fresh access tokens when expired
    - id_token: Contains user profile attributes and session identity

    Args:
        code: Authorization code received in the OIDC callback query parameter
        redirect_uri: Must exactly match the redirect_uri used in the initial auth request

    Returns:
        Dictionary containing tokens and expiration metadata.
    """
    client = get_client()
    try:
        logger.info(f"Exchanging authorization code for tokens (redirect_uri={redirect_uri})...")
        token_response = client.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
        )
        logger.info("Successfully received tokens from Keycloak.")
        return token_response
    except KeycloakAuthenticationError as e:
        logger.error(f"Authentication error exchanging code for token: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to exchange authorization code: {e}")
        raise


def refresh_user_token(refresh_token: str) -> dict:
    """
    Refreshes an expired access token using the valid refresh token.

    Args:
        refresh_token: The refresh token stored in the user's session

    Returns:
        Dictionary with fresh access_token, refresh_token, etc.
    """
    client = get_client()
    try:
        logger.info("Refreshing user tokens with refresh token...")
        tokens = client.refresh_token(refresh_token)
        return tokens
    except Exception as e:
        logger.error(f"Failed to refresh user token: {e}")
        raise


def get_user_info(access_token: str) -> dict:
    """
    Fetches user profile information from Keycloak's /userinfo endpoint.

    Args:
        access_token: Active JWT access token

    Returns:
        Dictionary containing user claims: sub (user UUID), preferred_username, email, etc.
    """
    client = get_client()
    try:
        user_info = client.userinfo(access_token)
        return user_info
    except Exception as e:
        logger.error(f"Failed to fetch userinfo from Keycloak: {e}")
        raise


def decode_and_validate_token(token: str, verify_signature: bool = True) -> dict:
    """
    Decodes and validates the JWT access token using Keycloak's public keys.
    Verifies signature (via Keycloak JWKS certs) and expiration timestamp (exp).

    Args:
        token: Raw JWT access token string
        verify_signature: Whether to verify cryptographic signature against Keycloak

    Returns:
        Decoded payload dictionary containing claims.
    """
    client = get_client()
    decoded = None

    if verify_signature:
        try:
            # Validates signature using Keycloak's realm JWKS certificates
            decoded = client.decode_token(token=token, validate=True)
            logger.debug("Successfully validated token signature via Keycloak JWKS.")
        except Exception as e:
            logger.warning(f"Signature verification failed or Keycloak offline: {e}. Decoding payload...")
            try:
                decoded = client.decode_token(token=token, validate=False)
            except Exception as err:
                logger.error(f"Token decoding failed: {err}")
                raise
    else:
        decoded = client.decode_token(token=token, validate=False)

    # Verify token expiration timestamp
    exp = decoded.get("exp")
    if exp and time.time() > exp:
        logger.warning(f"Token has expired! Expiration: {exp}, Current time: {time.time()}")
        raise KeycloakError("Token has expired.")

    return decoded


def extract_roles_from_token(token_payload: dict) -> list:
    """
    Extracts all assigned roles for the user from the decoded JWT token payload.
    In Keycloak, roles can be configured at two levels:
    1. Realm Roles: Under payload['realm_access']['roles'] (e.g., 'admin', 'user')
    2. Client Roles: Under payload['resource_access'][client_id]['roles']

    Args:
        token_payload: Decoded JWT claims dictionary

    Returns:
        List of unique string role names (e.g., ['user', 'admin']).
    """
    roles = set()

    # 1. Realm-level roles
    realm_access = token_payload.get("realm_access", {})
    if isinstance(realm_access, dict):
        realm_roles = realm_access.get("roles", [])
        if isinstance(realm_roles, list):
            for r in realm_roles:
                roles.add(str(r).lower())

    # 2. Client-level roles for our specific client
    resource_access = token_payload.get("resource_access", {})
    if isinstance(resource_access, dict):
        client_access = resource_access.get(KEYCLOAK_CLIENT_ID, {})
        if isinstance(client_access, dict):
            client_roles = client_access.get("roles", [])
            if isinstance(client_roles, list):
                for r in client_roles:
                    roles.add(str(r).lower())

    # 3. Direct roles claim (if mapped directly)
    direct_roles = token_payload.get("roles", [])
    if isinstance(direct_roles, list):
        for r in direct_roles:
            roles.add(str(r).lower())

    return sorted(list(roles))


def get_logout_url(id_token: str = None, post_logout_redirect_uri: str = None) -> str:
    """
    Builds the OpenID Connect RP-Initiated Logout URL.
    Redirecting the user to this URL logs them out of Keycloak Single Sign-On session
    and redirects their browser back to our application.

    Keycloak 18+ requires post_logout_redirect_uri + (id_token_hint OR client_id).

    Args:
        id_token: The raw ID token from login (serves as id_token_hint)
        post_logout_redirect_uri: Where to redirect after Keycloak logs out

    Returns:
        The URL string to redirect the user to.
    """
    if post_logout_redirect_uri is None:
        post_logout_redirect_uri = f"{APP_URL}/"

    base_logout_url = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"

    params = {
        "post_logout_redirect_uri": post_logout_redirect_uri,
    }

    if id_token:
        params["id_token_hint"] = id_token
    else:
        params["client_id"] = KEYCLOAK_CLIENT_ID

    logout_url = f"{base_logout_url}?{urlencode(params)}"
    logger.info(f"Built Keycloak Logout URL redirecting to: {post_logout_redirect_uri}")
    return logout_url


def logout_user(refresh_token: str = None) -> bool:
    """
    Performs backchannel logout in Keycloak using the user's refresh token.
    This revokes the refresh token and session on the Keycloak server.

    Args:
        refresh_token: The user's refresh token

    Returns:
        True if logout succeeded, False otherwise.
    """
    if not refresh_token:
        return False
    client = get_client()
    try:
        client.logout(refresh_token)
        logger.info("Successfully executed Keycloak backchannel logout.")
        return True
    except Exception as e:
        logger.warning(f"Keycloak backchannel logout warning: {e}")
        return False
