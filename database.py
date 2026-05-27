import os
import pandas as pd
import json
from datetime import datetime

CSV_PATH = os.path.join("data", "legajo.csv")
JSON_PATH = os.path.join("data", "solicitudes.json")

def cargar_datos():
    """Carga los datos del CSV de empleados."""
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()
    return pd.read_csv(CSV_PATH)

def guardar_datos(df):
    """Guarda los datos en el CSV de empleados."""
    df.to_csv(CSV_PATH, index=False)

def buscar_empleado(legajo: str) -> dict | None:
    """Busca un empleado por su número de legajo."""
    df = cargar_datos()
    if df.empty:
        return None
    # Convertimos el parámetro a string por seguridad
    legajo_str = str(legajo).zfill(3)
    # Buscamos comparando strings normalizados
    empleado = df[df['Legajo'].astype(str).str.zfill(3) == legajo_str]
    if not empleado.empty:
        return empleado.iloc[0].to_dict()
    return None

def obtener_empleados_sector(sector: str) -> list[dict]:
    """Obtiene todos los empleados de un sector específico."""
    df = cargar_datos()
    return df[df['Sector'] == sector].to_dict('records')

def cargar_solicitudes() -> list:
    """Carga el registro de solicitudes desde el JSON."""
    if not os.path.exists(JSON_PATH):
        return []
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("solicitudes", [])

def guardar_solicitudes(solicitudes: list):
    """Guarda la lista de solicitudes en el JSON."""
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump({"solicitudes": solicitudes}, f, indent=2, ensure_ascii=False)

def guardar_solicitud(solicitud: dict) -> str:
    """Registra una nueva solicitud y retorna su ID."""
    solicitudes = cargar_solicitudes()
    
    # Generar ID correlativo
    prox_id = len(solicitudes) + 1
    id_sol = f"SOL-{prox_id:03d}"
    
    solicitud["id"] = id_sol
    solicitud["fecha_solicitud"] = datetime.now().isoformat()
    solicitudes.append(solicitud)
    
    guardar_solicitudes(solicitudes)
    return id_sol

def actualizar_estado_solicitud(id_sol: str, nuevo_estado: str, motivo: str = "") -> bool:
    """Cambia el estado de una solicitud (APROBADA/RECHAZADA)."""
    solicitudes = cargar_solicitudes()
    for sol in solicitudes:
        if sol["id"] == id_sol:
            sol["estado"] = nuevo_estado
            if motivo:
                sol["motivo_rechazo"] = motivo
            guardar_solicitudes(solicitudes)
            return True
    return False

def descontar_dias(legajo: str, dias: int) -> bool:
    """Resta días de vacaciones del saldo del empleado en el CSV."""
    df = cargar_datos()
    idx = df[df['Legajo'].astype(str).str.zfill(3) == legajo.zfill(3)].index
    if not idx.empty:
        df.loc[idx, 'Días de vacaciones disponibles'] -= dias
        guardar_datos(df)
        return True
    return False

def obtener_solicitudes_pendientes() -> list[dict]:
    """Retorna todas las solicitudes con estado PENDIENTE."""
    solicitudes = cargar_solicitudes()
    return [s for s in solicitudes if s["estado"] == "PENDIENTE"]

def obtener_solicitud_por_id(id_sol: str) -> dict | None:
    """Busca una solicitud específica por su ID."""
    solicitudes = cargar_solicitudes()
    for s in solicitudes:
        if s["id"] == id_sol:
            return s
    return None

def hay_solicitud_pendiente(legajo: str) -> bool:
    """Verifica si un empleado ya tiene una solicitud en trámite."""
    solicitudes = cargar_solicitudes()
    for s in solicitudes:
        if s["legajo"].zfill(3) == legajo.zfill(3) and s["estado"] == "PENDIENTE":
            return True
    return False

def obtener_ultima_solicitud(legajo: str) -> dict | None:
    """Obtiene la solicitud más reciente de un empleado."""
    solicitudes = cargar_solicitudes()
    emp_sols = [s for s in solicitudes if s["legajo"].zfill(3) == legajo.zfill(3)]
    if emp_sols:
        return sorted(emp_sols, key=lambda x: x["fecha_solicitud"], reverse=True)[0]
    return None

def obtener_historial_empleado(legajo: str) -> list[dict]:
    """Obtiene todas las solicitudes de un empleado."""
    solicitudes = cargar_solicitudes()
    return [s for s in solicitudes if s["legajo"].zfill(3) == legajo.zfill(3)]
