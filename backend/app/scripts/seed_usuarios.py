import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal
from app.models.caso import Caso  # noqa: F401
from app.models.evento import Evento  # noqa: F401
from app.models.tarea import Tarea  # noqa: F401
from app.models.usuario import Usuario
from app.core.security import hash_password

usuarios = [
    {
        "nombre": "Gil Palmert",
        "email": "gilpalmert@ihuisystems.com",
        "hashed_password": hash_password("ihui2026!"),
        "rol": "superadmin",
        "activo": True,
    },
    {
        "nombre": "Leo",
        "email": "200300623@ucaribe.edu.mx",
        "hashed_password": hash_password("ihui2026!"),
        "rol": "intern",
        "activo": True,
    },
    {
        "nombre": "Aldo",
        "email": "yahiraldo11@gmail.com",
        "hashed_password": hash_password("ihui2026!"),
        "rol": "intern",
        "activo": True,
    },
]

db = SessionLocal()
try:
    for u in usuarios:
        existe = db.query(Usuario).filter(Usuario.email == u["email"]).first()
        if not existe:
            db.add(Usuario(**u))
            print(f"Creado: {u['email']}")
        else:
            print(f"Ya existe: {u['email']}")
    db.commit()
    print("Seed completado.")
finally:
    db.close()
