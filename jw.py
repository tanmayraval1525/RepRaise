import secrets

# Generate a secure random key
jwt_secret_key = secrets.token_hex(32)  # Generates a 32-byte key, represented as a hexadecimal string

print(f"Your JWT secret key: {jwt_secret_key}")