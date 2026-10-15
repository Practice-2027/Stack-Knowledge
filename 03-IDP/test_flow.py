"""
test_flow.py
============
Automated End-to-End Verification Suite for the Custom Identity Provider.

Tests:
1. IDP OIDC Discovery (/.well-known/openid-configuration)
2. IDP JWKS Public Key Set (/jwks)
3. User Registration (/register)
4. Direct User Login (/login)
5. OAuth 2.0 Authorization Code Flow (/authorize -> /token)
6. Token Refresh Grant (/token with refresh_token)
7. IDP UserInfo Endpoint (/userinfo)
8. Resource Server Profile Verification (/api/profile)
9. Resource Server Protected Data List & Creation (/api/data)
10. Security Checks: Tampered Token Rejection & Missing Header Rejection
"""

import sys
import time
import requests
import jwt

IDP_URL = "http://localhost:5003"
RESOURCE_URL = "http://localhost:5004"
CLIENT_URL = "http://localhost:5005"

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"


def run_tests():
    print("=" * 65)
    print("       STARTING IDP & RESOURCE SERVER END-TO-END TESTS          ")
    print("=" * 65)

    # Pre-check: Ensure servers are reachable
    print(f"{INFO} Checking if IDP server is reachable at {IDP_URL}...")
    try:
        r = requests.get(f"{IDP_URL}/", timeout=3)
        assert r.status_code == 200
        print(f"{PASS} IDP Server is online!")
    except Exception as e:
        print(f"{FAIL} IDP Server is NOT running at {IDP_URL}. Please start servers first!")
        print(f"       Run 'python run_all.py' in a separate terminal.")
        return False

    print(f"{INFO} Checking if Resource Server is reachable at {RESOURCE_URL}...")
    try:
        r = requests.get(f"{RESOURCE_URL}/api/health", timeout=3)
        assert r.status_code == 200
        print(f"{PASS} Resource Server is online!")
    except Exception as e:
        print(f"{FAIL} Resource Server is NOT running at {RESOURCE_URL}.")
        return False

    # 1. Test OIDC Discovery
    print(f"\n{INFO} Test 1: OpenID Connect Discovery (/.well-known/openid-configuration)...")
    r = requests.get(f"{IDP_URL}/.well-known/openid-configuration")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    disco = r.json()
    assert disco.get("issuer") == IDP_URL
    assert "jwks_uri" in disco
    print(f"{PASS} OIDC Discovery endpoint returned valid config with issuer: {disco['issuer']}")

    # 2. Test JWKS
    print(f"\n{INFO} Test 2: JSON Web Key Set (/jwks)...")
    r = requests.get(f"{IDP_URL}/jwks")
    assert r.status_code == 200
    jwks = r.json()
    assert "keys" in jwks and len(jwks["keys"]) > 0
    key = jwks["keys"][0]
    assert key.get("kty") == "RSA"
    assert key.get("alg") == "RS256"
    assert "n" in key and "e" in key
    print(f"{PASS} JWKS endpoint returned valid RSA public key (kid={key.get('kid')}, alg={key.get('alg')})")

    # 3. Test Registration
    print(f"\n{INFO} Test 3: User Registration (/register)...")
    test_user = f"tester_{int(time.time())}"
    r = requests.post(
        f"{IDP_URL}/register",
        json={"username": test_user, "email": f"{test_user}@test.com", "password": "password123", "full_name": "Test User"}
    )
    assert r.status_code == 201
    print(f"{PASS} Successfully registered new user '{test_user}'")

    # 4. Test Direct Login
    print(f"\n{INFO} Test 4: Direct Login (/login)...")
    r = requests.post(f"{IDP_URL}/login", json={"username": test_user, "password": "password123"})
    assert r.status_code == 200
    login_data = r.json()
    direct_token = login_data.get("access_token")
    refresh_token = login_data.get("refresh_token")
    assert direct_token and refresh_token
    print(f"{PASS} Direct login issued access_token and refresh_token")

    # 5. Test Dedicated Refresh Token Endpoint
    print(f"\n{INFO} Test 5: Dedicated Refresh Token Endpoint (/token/refresh)...")
    r = requests.post(f"{IDP_URL}/token/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    new_access_token = r.json().get("access_token")
    assert new_access_token
    print(f"{PASS} Successfully issued new access token via refresh token")

    # 6. Test OAuth 2.0 Authorization Code Flow
    print(f"\n{INFO} Test 6: OAuth 2.0 Authorization Code Flow (/authorize -> /token)...")
    # Step A: POST to /authorize to simulate user login on consent page
    auth_resp = requests.post(
        f"{IDP_URL}/authorize",
        data={
            "action": "login",
            "username": "alice",
            "password": "password123",
            "client_id": "client_app_demo",
            "redirect_uri": "http://localhost:5005/callback",
            "state": "test_state_123",
            "scope": "openid profile email read write"
        },
        allow_redirects=False
    )
    assert auth_resp.status_code == 302, f"Expected 302 redirect, got {auth_resp.status_code}"
    redirect_location = auth_resp.headers.get("Location", "")
    assert "code=" in redirect_location
    assert "state=test_state_123" in redirect_location

    # Extract auth code
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect_location)
    params = parse_qs(parsed.query)
    auth_code = params.get("code", [None])[0]
    assert auth_code is not None
    print(f"{PASS} Submitting credentials redirected with auth_code: {auth_code[:16]}...")

    # Step B: Exchange auth_code for tokens at /token
    token_resp = requests.post(
        f"{IDP_URL}/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": "client_app_demo",
            "client_secret": "super-secret-client-password",
            "redirect_uri": "http://localhost:5005/callback"
        }
    )
    assert token_resp.status_code == 200, f"Token exchange failed: {token_resp.text}"
    token_data = token_resp.json()
    oauth_access_token = token_data.get("access_token")
    oauth_refresh_token = token_data.get("refresh_token")
    oauth_id_token = token_data.get("id_token")
    assert oauth_access_token and oauth_refresh_token and oauth_id_token
    print(f"{PASS} Code exchange succeeded! Received access_token, id_token, and refresh_token")

    # Step C: Verify Single-Use Code Policy (Replay Attack Prevention)
    replay_resp = requests.post(
        f"{IDP_URL}/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": "client_app_demo"
        }
    )
    assert replay_resp.status_code == 400
    print(f"{PASS} Replay attack prevented: Code cannot be used twice")

    # 7. Test UserInfo Endpoint
    print(f"\n{INFO} Test 7: UserInfo Endpoint (/userinfo)...")
    ui_resp = requests.get(
        f"{IDP_URL}/userinfo",
        headers={"Authorization": f"Bearer {oauth_access_token}"}
    )
    assert ui_resp.status_code == 200
    ui = ui_resp.json()
    assert ui.get("sub") == "alice"
    assert ui.get("email") == "alice@example.com"
    print(f"{PASS} /userinfo returned claims for subject: {ui.get('sub')} ({ui.get('email')})")

    # 8. Test Resource Server: Profile Verification with JWKS
    print(f"\n{INFO} Test 8: Resource Server Profile Endpoint (/api/profile)...")
    res_prof_resp = requests.get(
        f"{RESOURCE_URL}/api/profile",
        headers={"Authorization": f"Bearer {oauth_access_token}"}
    )
    assert res_prof_resp.status_code == 200, f"Resource server rejected token: {res_prof_resp.text}"
    res_prof = res_prof_resp.json()
    assert res_prof.get("status") == "success"
    assert res_prof["user"]["username"] == "alice"
    print(f"{PASS} Resource server validated JWT using JWKS! Subject: {res_prof['user']['username']}")

    # 9. Test Resource Server: Protected Data List & Creation
    print(f"\n{INFO} Test 9: Resource Server Protected Data (/api/data)...")
    # GET data
    data_resp = requests.get(
        f"{RESOURCE_URL}/api/data",
        headers={"Authorization": f"Bearer {oauth_access_token}"}
    )
    assert data_resp.status_code == 200
    docs = data_resp.json().get("documents", [])
    initial_count = len(docs)
    print(f"{PASS} GET /api/data returned {initial_count} document(s) for alice")

    # POST new document
    new_doc_title = f"Automated Test Record {int(time.time())}"
    create_resp = requests.post(
        f"{RESOURCE_URL}/api/data",
        headers={"Authorization": f"Bearer {oauth_access_token}"},
        json={"title": new_doc_title, "content": "Verified cryptographically by resource server.", "category": "Testing"}
    )
    assert create_resp.status_code == 201
    created_id = create_resp.json()["document"]["id"]
    print(f"{PASS} POST /api/data created new document id={created_id} ('{new_doc_title}')")

    # 10. Security Checks
    print(f"\n{INFO} Test 10: Security Checks (Missing Token, Tampered Signature)...")
    # Missing Token
    no_token_resp = requests.get(f"{RESOURCE_URL}/api/profile")
    assert no_token_resp.status_code == 401
    print(f"{PASS} Resource server correctly rejected unauthenticated request (401)")

    # Tampered Token (modify payload character)
    parts = oauth_access_token.split(".")
    tampered_token = f"{parts[0]}.eyJhZG1pbiI6dHJ1ZX0.{parts[2]}"
    tampered_resp = requests.get(
        f"{RESOURCE_URL}/api/profile",
        headers={"Authorization": f"Bearer {tampered_token}"}
    )
    assert tampered_resp.status_code == 401
    print(f"{PASS} Resource server correctly rejected cryptographically tampered token (401)")

    print("\n" + "=" * 65)
    print("        ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY!          ")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
