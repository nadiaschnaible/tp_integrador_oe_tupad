from datetime import datetime, date, timedelta
import database

MAX_DIAS_VACACIONES = 30  # Límite razonable por solicitud

def validar_formato_fecha(texto: str) -> date | None:
    """Valida que el texto sea una fecha en formato DD/MM/AAAA."""
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        return None

def validar_rango_razonable(inicio: date, fin: date) -> bool:
    """Verifica que el rango de fechas no sea absurdamente largo."""
    dias = calcular_dias_solicitados(inicio, fin)
    return dias <= MAX_DIAS_VACACIONES

def validar_fecha_futura(fecha: date, dias_minimos: int = 5) -> bool:
    """
    REGLA 4: La fecha de inicio debe ser al menos 5 días hábiles en el futuro.
    Para simplificar, usamos días corridos en este cálculo.
    """
    hoy = date.today()
    minima_fecha = hoy + timedelta(days=dias_minimos)
    return fecha >= minima_fecha

def calcular_dias_solicitados(inicio: date, fin: date) -> int:
    """
    REGLA 3: Días corridos para el cálculo del consumo.
    """
    if fin < inicio:
        return 0
    return (fin - inicio).days + 1

def validar_saldo(legajo: str, dias: int) -> tuple[bool, int]:
    """
    REGLA 1: Verifica si el empleado tiene saldo suficiente.
    """
    empleado = database.buscar_empleado(str(legajo))
    if not empleado:
        return False, 0
    
    saldo_actual = int(empleado["Días de vacaciones disponibles"])
    return dias <= saldo_actual, saldo_actual

def verificar_restriccion_jerarquia(legajo: str, inicio: date, fin: date) -> tuple[bool, str]:
    """
    REGLA 6: El Director y el Subdirector no pueden estar de vacaciones simultáneamente.
    Legajos: 1 (Director), 2 (Subdirectora).
    """
    legajo_str = str(legajo).zfill(3)
    if legajo_str not in ["001", "002"]:
        return True, ""
    
    # Identificar quién es el "par" a controlar
    legajo_par = "002" if legajo_str == "001" else "001"
    rol_par = "Subdirectora" if legajo_str == "001" else "Director"
    
    solicitudes = database.cargar_solicitudes()
    for sol in solicitudes:
        if sol["legajo"].zfill(3) == legajo_par and sol["estado"] in ["PENDIENTE", "APROBADA"]:
            sol_inicio = datetime.fromisoformat(sol["fecha_inicio"]).date()
            sol_fin = datetime.fromisoformat(sol["fecha_fin"]).date()
            
            # Verificar solapamiento
            if max(inicio, sol_inicio) <= min(fin, sol_fin):
                return False, f"Conflicto de jerarquía: El {rol_par} ya tiene una solicitud en ese período."
    
    return True, ""

def verificar_restriccion_sector(sector: str, inicio: date, fin: date) -> tuple[bool, str]:
    """
    REGLA 2: No puede estar ausente más del 50% de un mismo sector simultáneamente.
    """
    empleados_sector = database.obtener_empleados_sector(sector)
    total_sector = len(empleados_sector)
    
    if total_sector == 0:
        return True, ""

    solicitudes = database.cargar_solicitudes()
    ausentes_en_rango = 0
    
    for sol in solicitudes:
        if sol["sector"] == sector and sol["estado"] in ["PENDIENTE", "APROBADA"]:
            sol_inicio = datetime.fromisoformat(sol["fecha_inicio"]).date()
            sol_fin = datetime.fromisoformat(sol["fecha_fin"]).date()
            
            # Verificar solapamiento de fechas
            if max(inicio, sol_inicio) <= min(fin, sol_fin):
                ausentes_en_rango += 1

    # Incluimos a la persona que está solicitando ahora
    ausentes_totales = ausentes_en_rango + 1
    
    # GATEWAY: ¿Supera el 50%?
    if ausentes_totales > (total_sector / 2):
        return False, f"Conflicto operativo: Ya hay {ausentes_en_rango} personas ausentes en ese período en {sector}."
    
    return True, ""
