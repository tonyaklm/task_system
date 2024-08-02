from passlib.context import CryptContext

password_context = CryptContext(schemes=["sha256_crypt", "md5_crypt"])


def encrypt_password(password: str) -> str:
    """ Encrypts password"""

    return password_context.encrypt(password)


def check_encrypted_password(password: str, hashed: str) -> bool:
    """ Decrypts password"""

    return password_context.verify(password, hashed)
