from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

@router.post("/login")
def login(
    request: Request,
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == form.username).first()
    if not usuario or not verify_password(form.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    ip = get_client_ip(request)

    token = create_access_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol,
        "ip": ip,
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # True en producción con HTTPS
        samesite="lax",
        max_age=60 * 480,
    )

    return {
        "status": "ok",
        "usuario": {
            "id": str(usuario.id),
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol,
        }
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "ok"}

@router.get("/me")
def me(request: Request, current_user: Usuario = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "nombre": current_user.nombre,
        "email": current_user.email,
        "rol": current_user.rol,
        "activo": current_user.activo,
    }
