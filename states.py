from enum import IntEnum

class State(IntEnum):
    LEGAJO = 0        # Esperando número de legajo
    FECHA_INICIO = 1  # Esperando fecha de inicio
    FECHA_FIN = 2     # Esperando fecha de fin
    CONFIRMACION = 3  # Mostrando resumen y pidiendo confirmación
    FIN = 4           # Conversación terminada
