from ..config.settings import PASSWORD_SALT
import hashlib

class User:
    @staticmethod
    def _hash_password(password: str) -> str:
        """Genera hash SHA-256 con salt estático"""
        if not PASSWORD_SALT:
            raise ValueError("Salt de contraseña no configurado")
        return hashlib.sha256(
            f"{password}--{PASSWORD_SALT}".encode('utf-8')
        ).hexdigest()