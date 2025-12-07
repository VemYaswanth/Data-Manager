import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from core.config import BASE_DIR

KEY_PATH = os.path.join(BASE_DIR, "encryption", "vault.key")

# Ensure encryption folder exists
os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)

def load_or_create_key():
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            return f.read()
    
    key = get_random_bytes(32)  # AES-256
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    return key

KEY = load_or_create_key()


def pad(data):
    pad_len = 16 - (data.len % 16)
    return data + bytes([pad_len] * pad_len)


def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]


def encrypt_bytes(raw_bytes):
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)

    # Pad before encrypt
    pad_len = 16 - (len(raw_bytes) % 16)
    raw_padded = raw_bytes + bytes([pad_len] * pad_len)

    encrypted = cipher.encrypt(raw_padded)

    # Store IV + encrypted together
    return iv + encrypted


def decrypt_bytes(enc_bytes):
    iv = enc_bytes[:16]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)

    decrypted_padded = cipher.decrypt(enc_bytes[16:])
    pad_len = decrypted_padded[-1]
    return decrypted_padded[:-pad_len]