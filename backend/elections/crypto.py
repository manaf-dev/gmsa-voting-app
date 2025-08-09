"""
Cryptographic utilities for secure voting system
Provides encryption/decryption and digital signature capabilities
"""

import hashlib
import hmac
import secrets
from typing import Dict, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from django.conf import settings
import base64
import json


class VotingCrypto:
    """Enhanced cryptographic utilities for secure voting"""

    def __init__(self):
        # Generate or load encryption keys
        self.symmetric_key = self._get_or_generate_symmetric_key()
        self.cipher_suite = Fernet(self.symmetric_key)

    def _get_or_generate_symmetric_key(self) -> bytes:
        """Get symmetric encryption key from settings or generate new one.
        Accepts either a base64 urlsafe Fernet key (recommended) or a raw 32-byte key
        and converts it to base64. Falls back to generating a new key if invalid.
        """
        key_setting = getattr(settings, "VOTING_ENCRYPTION_KEY", None)
        if key_setting:
            # Normalize to bytes
            key_bytes = (
                key_setting if isinstance(key_setting, (bytes, bytearray)) else str(key_setting).encode()
            )

            # Case 1: Already a base64-urlsafe Fernet key that decodes to 32 bytes
            try:
                decoded = base64.urlsafe_b64decode(key_bytes)
                if len(decoded) == 32:
                    return key_bytes
            except Exception:
                pass

            # Case 2: Provided a raw 32-byte key -> encode to base64
            if len(key_bytes) == 32:
                return base64.urlsafe_b64encode(key_bytes)

            # Case 3: Provided a hex string of 64 chars -> convert to bytes then base64
            try:
                if len(key_bytes) == 64 and all(chr(c) in b"0123456789abcdefABCDEF" for c in key_bytes):
                    raw = bytes.fromhex(key_bytes.decode())
                    if len(raw) == 32:
                        return base64.urlsafe_b64encode(raw)
            except Exception:
                pass

            # If we reach here, the provided key is invalid; fall through to generate

        # Generate new key (should be persisted in production)
        return Fernet.generate_key()

    def encrypt_vote_data(self, vote_data: Dict) -> str:
        """
        Encrypt vote data with additional integrity checks
        Returns base64 encoded encrypted data
        """
        # Add timestamp and nonce for additional security
        enhanced_data = {
            "vote_data": vote_data,
            "nonce": secrets.token_hex(16),
            "timestamp": str(vote_data.get("timestamp", "")),
        }

        # Serialize and encrypt
        json_data = json.dumps(enhanced_data).encode()
        encrypted_data = self.cipher_suite.encrypt(json_data)

        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_vote_data(self, encrypted_data: str) -> Dict:
        """
        Decrypt vote data and verify integrity
        """
        try:
            # Decode and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            enhanced_data = json.loads(decrypted_data.decode())
            return enhanced_data["vote_data"]
        except Exception as e:
            raise ValueError(f"Failed to decrypt vote data: {str(e)}")

    def generate_vote_hash(
        self,
        voter_id: str,
        candidate_id: str,
        position_id: str,
        election_id: str,
        timestamp: str,
    ) -> str:
        """
        Generate cryptographic hash for vote integrity
        """
        vote_string = (
            f"{voter_id}:{candidate_id}:{position_id}:{election_id}:{timestamp}"
        )

        # Use HMAC with secret key for additional security
        secret_key = getattr(
            settings, "VOTE_HASH_SECRET", "default-secret-key"
        ).encode()
        vote_hash = hmac.new(
            secret_key, vote_string.encode(), hashlib.sha256
        ).hexdigest()

        return vote_hash

    def verify_vote_integrity(
        self,
        vote_hash: str,
        voter_id: str,
        candidate_id: str,
        position_id: str,
        election_id: str,
        timestamp: str,
    ) -> bool:
        """
        Verify vote integrity using cryptographic hash
        """
        expected_hash = self.generate_vote_hash(
            voter_id, candidate_id, position_id, election_id, timestamp
        )

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(vote_hash, expected_hash)

    def anonymize_voter_data(self, voter_id: str, election_id: str, position_id: str) -> str:
        """
        Create anonymous voter token for privacy
        """
        # Combine voter ID with election ID and secret salt
        salt = getattr(settings, "VOTER_ANONYMIZATION_SALT", "default-salt")
        combined_data = f"{voter_id}:{election_id}:{position_id}:{salt}"
        # Create irreversible hash
        anonymous_token = hashlib.sha256(combined_data.encode()).hexdigest()[:16]

        return f"anon_{anonymous_token}"

    def generate_election_audit_hash(self, election_data: Dict) -> str:
        """
        Generate audit hash for election integrity
        """
        # Sort data to ensure consistent hashing
        sorted_data = json.dumps(election_data, sort_keys=True)

        return hashlib.sha256(sorted_data.encode()).hexdigest()


class DigitalSignature:
    """Digital signature utilities for vote verification"""

    def __init__(self):
        self.private_key, self.public_key = self._load_or_generate_keys()

    def _load_or_generate_keys(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Load existing keys or generate new RSA key pair"""
        try:
            # In production, load keys from secure storage
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048, backend=default_backend()
            )
            public_key = private_key.public_key()

            return private_key, public_key
        except Exception:
            # Fallback key generation
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048, backend=default_backend()
            )
            return private_key, private_key.public_key()

    def sign_vote(self, vote_data: bytes) -> bytes:
        """
        Create digital signature for vote data
        """
        signature = self.private_key.sign(
            vote_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        return signature

    def verify_vote_signature(self, vote_data: bytes, signature: bytes) -> bool:
        """
        Verify digital signature of vote data
        """
        try:
            self.public_key.verify(
                signature,
                vote_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


# Security configuration checker
def check_security_configuration() -> Dict[str, bool]:
    """
    Check if security settings are properly configured
    """
    checks = {
        "encryption_key_set": hasattr(settings, "VOTING_ENCRYPTION_KEY"),
        "hash_secret_set": hasattr(settings, "VOTE_HASH_SECRET"),
        "salt_configured": hasattr(settings, "VOTER_ANONYMIZATION_SALT"),
        "secure_cookies": getattr(settings, "SESSION_COOKIE_SECURE", False),
        "csrf_protection": "django.middleware.csrf.CsrfViewMiddleware"
        in getattr(settings, "MIDDLEWARE", []),
        "https_redirect": getattr(settings, "SECURE_SSL_REDIRECT", False),
    }

    return checks


# Audit trail utilities
def create_audit_entry(
    action: str,
    user_id: str,
    resource_type: str,
    resource_id: str,
    details: Dict = None,
) -> Dict:
    """
    Create standardized audit entry
    """
    import time

    return {
        "timestamp": time.time(),
        "action": action,
        "user_id": user_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
        "ip_address": None,  # Will be set by view
        "user_agent": None,  # Will be set by view
    }
