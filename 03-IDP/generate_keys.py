"""
generate_keys.py
================
Generates an RSA 2048-bit key pair (private and public keys) used for
signing and verifying JSON Web Tokens (JWT) using the RS256 algorithm.

Why Asymmetric Cryptography (RSA)?
-----------------------------------
- The Identity Provider (IDP) keeps the PRIVATE key secret to SIGN tokens.
- The Resource Server and clients use the PUBLIC key to VERIFY tokens.
- This means the Resource Server NEVER needs the private key! It can independently
  verify that tokens are authentic without having the power to forge them.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Target directory defaults to current directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "public_key.pem")


def generate_rsa_keypair(private_path=PRIVATE_KEY_PATH, public_path=PUBLIC_KEY_PATH, force=False):
    """
    Generates an RSA 2048-bit key pair and saves them as PEM files.
    
    Args:
        private_path: Path to write private_key.pem
        public_path: Path to write public_key.pem
        force: If True, regenerates keys even if they already exist.
    
    Returns:
        tuple: (private_key_pem_bytes, public_key_pem_bytes)
    """
    if not force and os.path.exists(private_path) and os.path.exists(public_path):
        print(f"[KEYS] Keys already exist:\n  - Private: {private_path}\n  - Public:  {public_path}")
        with open(private_path, "rb") as f:
            priv = f.read()
        with open(public_path, "rb") as f:
            pub = f.read()
        return priv, pub

    print("[KEYS] Generating new 2048-bit RSA key pair...")

    # 1. Generate private key (2048-bit is standard for RS256)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 2. Serialize private key to PEM format (PKCS#8, unencrypted for local demo)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 3. Extract public key and serialize to PEM format (SubjectPublicKeyInfo)
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # 4. Save to files
    with open(private_path, "wb") as f:
        f.write(private_pem)

    with open(public_path, "wb") as f:
        f.write(public_pem)

    print(f"[KEYS] Key pair generated successfully!")
    print(f"[KEYS] -> Private key saved to: {private_path}")
    print(f"[KEYS] -> Public key saved to:  {public_path}")
    return private_pem, public_pem


def ensure_keys_exist():
    """Helper to ensure RSA keys exist prior to server startup."""
    return generate_rsa_keypair(force=False)


if __name__ == "__main__":
    print("=" * 65)
    print("      RSA KEY PAIR GENERATOR FOR IDENTITY PROVIDER (RS256)     ")
    print("=" * 65)
    print("About RSA & JWT Signing:")
    print("  * RS256 uses asymmetric cryptography (Private Key + Public Key).")
    print("  * Private Key (private_key.pem): Kept secret on IDP server.")
    print("  * Public Key  (public_key.pem):  Published via /jwks endpoint.")
    print("  * Anyone can verify tokens with the Public Key, but only")
    print("    the IDP can create tokens using the Private Key.")
    print("-" * 65)
    generate_rsa_keypair(force=True)
    print("=" * 65)
    print("Setup complete! You can now start the IDP server.")
