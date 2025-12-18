"""
Environment file encryption/decryption utility using Fernet (AES-128-CBC)
"""
import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_fernet_key(password: str, salt: bytes = b'serfor_env_salt_2024') -> bytes:
    """
    Derive a Fernet-compatible key from a password using PBKDF2.

    Args:
        password: The encryption password/key
        salt: Salt for key derivation

    Returns:
        A 32-byte base64-encoded key suitable for Fernet
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_env_file(input_path: str, output_path: str, encryption_key: str) -> bool:
    """
    Encrypt a .env file.

    Args:
        input_path: Path to the plaintext .env file
        output_path: Path to save the encrypted file
        encryption_key: The encryption password

    Returns:
        True if successful, False otherwise
    """
    try:
        key = get_fernet_key(encryption_key)
        fernet = Fernet(key)

        with open(input_path, 'rb') as f:
            plaintext = f.read()

        encrypted = fernet.encrypt(plaintext)

        with open(output_path, 'wb') as f:
            f.write(encrypted)

        return True
    except Exception as e:
        print(f"Encryption error: {e}")
        return False


def decrypt_env_file(input_path: str, output_path: str = None, encryption_key: str = None) -> str | None:
    """
    Decrypt an encrypted .env file.

    Args:
        input_path: Path to the encrypted file
        output_path: Optional path to save decrypted content (if None, returns content)
        encryption_key: The encryption password (if None, reads from ENV_ENCRYPTION_KEY)

    Returns:
        Decrypted content as string if output_path is None, else None
    """
    if encryption_key is None:
        encryption_key = os.environ.get('ENV_ENCRYPTION_KEY')
        if not encryption_key:
            raise ValueError("ENV_ENCRYPTION_KEY environment variable not set")

    try:
        key = get_fernet_key(encryption_key)
        fernet = Fernet(key)

        with open(input_path, 'rb') as f:
            encrypted = f.read()

        decrypted = fernet.decrypt(encrypted)

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            return None

        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return None


def load_encrypted_env(encrypted_path: str, encryption_key: str = None) -> dict:
    """
    Load environment variables from an encrypted .env file.

    Args:
        encrypted_path: Path to the encrypted .env file
        encryption_key: The encryption password (if None, reads from ENV_ENCRYPTION_KEY)

    Returns:
        Dictionary of environment variables
    """
    content = decrypt_env_file(encrypted_path, encryption_key=encryption_key)
    if content is None:
        return {}

    env_vars = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            # Remove quotes if present
            value = value.strip()
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            env_vars[key.strip()] = value

    return env_vars


def inject_encrypted_env(encrypted_path: str, encryption_key: str = None) -> bool:
    """
    Load encrypted env file and inject variables into os.environ.

    Args:
        encrypted_path: Path to the encrypted .env file
        encryption_key: The encryption password

    Returns:
        True if successful, False otherwise
    """
    try:
        env_vars = load_encrypted_env(encrypted_path, encryption_key)
        for key, value in env_vars.items():
            os.environ[key] = value
        return True
    except Exception as e:
        print(f"Error injecting encrypted env: {e}")
        return False
