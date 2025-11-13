# auth.py
import os
import hashlib
import base64
import uuid
import platform

MASTER_FILE = "diary_data/master.key"
SALT_FILE = "diary_data/salt.bin"
DEVICE_FILE = "diary_data/device.lock"
KDF_ITERATIONS = 200_000

def get_kek(password: str) -> bytes:
    """Key-encryption-key derived from master password + salt.bin"""
    if not os.path.exists(SALT_FILE):
        raise FileNotFoundError("Salt file missing! Diary cannot be decrypted.")
    with open(SALT_FILE, "rb") as f:
        salt = f.read()
    return get_key_from_password(password, salt)

def generate_salt():
    return os.urandom(16)


def get_key_from_password(password: str, salt: bytes) -> bytes:
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, KDF_ITERATIONS, dklen=32)
    return base64.urlsafe_b64encode(key)


def get_device_id() -> str:
    sys_info = platform.node() + platform.system() + str(uuid.getnode())
    return hashlib.sha256(sys_info.encode()).hexdigest()[:32]


def create_master_password(password: str):
    if not os.path.exists("diary_data"):
        os.makedirs("diary_data", exist_ok=True)

    salt = generate_salt()
    key = get_key_from_password(password, salt)

    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    with open(MASTER_FILE, "wb") as f:
        f.write(key)
    with open(DEVICE_FILE, "w") as f:
        f.write(get_device_id())


def verify_master_password(password: str) -> bool:
    if not os.path.exists(MASTER_FILE) or not os.path.exists(SALT_FILE):
        return False
    try:
        with open(SALT_FILE, "rb") as f:
            salt = f.read()
        derived = get_key_from_password(password, salt)
        with open(MASTER_FILE, "rb") as f:
            stored = f.read()

        if os.path.exists(DEVICE_FILE):
            with open(DEVICE_FILE, "r") as f:
                saved_dev = f.read().strip()
            if saved_dev != get_device_id():
                return False

        return derived == stored
    except Exception:
        return False


def check_password_strength(password: str) -> tuple[str, str]:
    """Returns (strength_level, color) tuple"""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    
    if score <= 2:
        return ("Weak", "#FF4444")
    elif score <= 4:
        return ("Medium", "#FFA500")
    else:
        return ("Strong", "#00FF00")