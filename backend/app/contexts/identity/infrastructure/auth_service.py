"""Implementación de AuthService: Argon2id para contraseñas, HS256 para JWT."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.shared.domain.base import AuthenticationError


class ArgonAuthService:
    def __init__(self, secret_key: str, expire_minutes: int) -> None:
        self._ph = PasswordHasher()
        self._secret_key = secret_key
        self._expire_minutes = expire_minutes

    def hash_password(self, plain: str) -> str:
        return self._ph.hash(plain)

    def verify_password(self, plain: str, hashed: str) -> bool:
        try:
            return self._ph.verify(hashed, plain)
        except VerifyMismatchError:
            return False

    def create_access_token(self, subject: str, rol: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        payload = {"sub": subject, "rol": rol, "exp": expire}
        return jwt.encode(payload, self._secret_key, algorithm="HS256")

    def decode_token(self, token: str) -> dict[str, str]:
        try:
            data: dict[str, str] = jwt.decode(token, self._secret_key, algorithms=["HS256"])
            return data
        except JWTError:
            raise AuthenticationError("Token inválido o expirado.")
