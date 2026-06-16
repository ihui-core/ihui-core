"""
Punto único de decisión para permisos de asignación de tareas.

HOY: lista simple de roles que pueden asignar.
MAÑANA: cuando exista organigrama, solo se cambia el interior de
puede_asignar() sin tocar el resto del sistema.
"""

# Roles que pueden asignar tareas a otros usuarios
ROLES_PUEDEN_ASIGNAR = {
    "superadmin",
    "notario",
    "cfo",
    "coordinador",
    "abogado",
}

def puede_asignar(usuario) -> bool:
    """¿Este usuario puede asignar tareas a otros?

    Hoy: revisa si su rol está en la lista.
    Mañana: reemplazar por consulta a organigrama / cadena de mando.
    """
    return usuario.rol in ROLES_PUEDEN_ASIGNAR

def puede_derivar(usuario, tarea_padre) -> bool:
    """¿Este usuario puede derivar tareas hijas de esta tarea padre?

    Sí, si:
    - Es supervisor global (puede_asignar), O
    - Es el dueño del expediente de la tarea padre (dueno_ref), O
    - Es el responsable de la tarea padre
    """
    if puede_asignar(usuario):
        return True
    if tarea_padre.dueno_ref and tarea_padre.dueno_ref in (usuario.email, usuario.nombre):
        return True
    if tarea_padre.responsable_ref and tarea_padre.responsable_ref in (usuario.email, usuario.nombre):
        return True
    return False
