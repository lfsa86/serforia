#!/usr/bin/env python3
"""
Script to encrypt/decrypt .env files

Usage:
    # Encrypt
    python scripts/env_encrypt.py encrypt --key "your_secret_key"

    # Decrypt (for verification)
    python scripts/env_encrypt.py decrypt --key "your_secret_key"

    # Generate a random key
    python scripts/env_encrypt.py generate-key
"""
import sys
import os
import secrets
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.env_crypto import encrypt_env_file, decrypt_env_file


def generate_key():
    """Generate a secure random key"""
    return secrets.token_hex(32)


def main():
    parser = argparse.ArgumentParser(description='Encrypt/decrypt .env files')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt .env file')
    encrypt_parser.add_argument('--key', '-k', required=True, help='Encryption key')
    encrypt_parser.add_argument('--input', '-i', default='.env', help='Input file (default: .env)')
    encrypt_parser.add_argument('--output', '-o', default='.env.encrypted', help='Output file (default: .env.encrypted)')

    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt .env.encrypted file')
    decrypt_parser.add_argument('--key', '-k', required=True, help='Encryption key')
    decrypt_parser.add_argument('--input', '-i', default='.env.encrypted', help='Input file (default: .env.encrypted)')
    decrypt_parser.add_argument('--output', '-o', help='Output file (optional, prints to stdout if not specified)')

    # Generate key command
    subparsers.add_parser('generate-key', help='Generate a random encryption key')

    args = parser.parse_args()

    if args.command == 'generate-key':
        key = generate_key()
        print(f"Generated encryption key:\n{key}")
        print("\nSave this key securely! You'll need it to decrypt the file.")
        print("Set it as ENV_ENCRYPTION_KEY environment variable on your server.")
        return

    if args.command == 'encrypt':
        if not Path(args.input).exists():
            print(f"Error: Input file '{args.input}' not found")
            sys.exit(1)

        success = encrypt_env_file(args.input, args.output, args.key)
        if success:
            print(f"Successfully encrypted '{args.input}' -> '{args.output}'")
            print(f"\nNext steps:")
            print(f"1. Set ENV_ENCRYPTION_KEY={args.key} on your server")
            print(f"2. Deploy '{args.output}' to your server")
            print(f"3. Remove '{args.input}' from production (keep for local dev)")
        else:
            print("Encryption failed")
            sys.exit(1)
        return

    if args.command == 'decrypt':
        if not Path(args.input).exists():
            print(f"Error: Input file '{args.input}' not found")
            sys.exit(1)

        if args.output:
            result = decrypt_env_file(args.input, args.output, args.key)
            if result is None and Path(args.output).exists():
                print(f"Successfully decrypted '{args.input}' -> '{args.output}'")
            else:
                print("Decryption failed")
                sys.exit(1)
        else:
            content = decrypt_env_file(args.input, encryption_key=args.key)
            if content:
                print("Decrypted content:")
                print("-" * 40)
                print(content)
            else:
                print("Decryption failed")
                sys.exit(1)
        return

    parser.print_help()


if __name__ == '__main__':
    main()
