from passlib.context import CryptContext

context = CryptContext('argon2')


def hash(secret: str):
    return context.hash(secret)


def verify(secret: str, digest: str) -> bool:
    return context.verify(secret, digest)
