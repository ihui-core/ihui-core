# Reglas de estados de caso

Los casos de IHUI Core utilizan los siguientes estados operativos:

- ABIERTO
- EN_PROCESO
- PENDIENTE
- RESUELTO
- CERRADO

## Reglas de transición

Las transiciones permitidas son las siguientes:

- ABIERTO -> EN_PROCESO
- EN_PROCESO -> PENDIENTE
- EN_PROCESO -> RESUELTO
- PENDIENTE -> RESUELTO
- PENDIENTE -> CERRADO
- RESUELTO -> CERRADO

## Reglas prohibidas

No se permiten transiciones hacia atrás en los estados finales:

- CERRADO -> ABIERTO
- RESUELTO -> ABIERTO

Si una transición no está permitida, el backend devuelve un error de validación.
