from datetime import UTC, datetime, timedelta
from loguru import logger
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.config.settings import Settings

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/token",
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    """Create JWT"""
    data_to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=data_to_encode,
        algorithm=settings.algorythm,
        key=settings.secret_key.get_secret_value(),
    )
    logger.info("Created TOKEN")
    return encoded_jwt


# Verify token
def verify_access_token(token: str, settings: Settings) -> str | None:
    """Verify a JWT access token and return user_id in subject if valid or none if invalid"""
    logger.info("Verifying TOKEN")

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.secret_key.get_secret_value(),
            algorithms=[settings.algorythm],
            options={"require": ["exp", "sub"]},
        )
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        logger.info("Invalid or expired token")
        return None
    logger.info("Positive TOKEN verification")
    return payload.get("sub")
