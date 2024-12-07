import secrets
secret_key = secrets.token_hex(16)  # menghasilkan 32 karakter acak hex
print(secret_key)
