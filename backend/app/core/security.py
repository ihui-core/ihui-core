from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt as _bcrypt
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode()[:72], hashed.encode())

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode()[:72], _bcrypt.gensalt(rounds=12)).decode()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def _extract_token(request: Request, bearer_token: str | None) -> str | None:
    # Primero cookie httpOnly
    cookie = request.cookies.get("access_token")
    if cookie:
        return cookie
    # Fallback Bearer (para herramientas como curl/Swagger)
    return bearer_token

def get_current_user(
    request: Request,
    bearer_token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    from app.models.usuario import Usuario

    token = _extract_token(request, bearer_token)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_ip = payload.get("ip")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Validar anclaje de IP
    if token_ip and token_ip != "unknown":
        client_ip = _get_client_ip(request)
        if client_ip != token_ip:
            raise HTTPException(status_code=401, detail="Sesión inválida — IP no coincide")

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return usuario

def require_superadmin(current_user=Depends(get_current_user)):
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=403, detail="Se requiere rol superadmin")
    return current_user
