from passlib.hash import argon2


class Hasher:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return argon2.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return argon2.hash(password)
