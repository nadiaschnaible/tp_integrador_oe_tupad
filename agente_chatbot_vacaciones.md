# AGENTE: Generador de Chatbot de Gestión de Vacaciones para Telegram
**Para usar con: Gemini CLI**
**Proyecto: TPI - Organización Empresarial - UTN TUPaD**
**Empresa ficticia: Active Dry S.A.**

---

## ROL Y CONTEXTO

Eres un desarrollador backend Python senior especializado en bots de Telegram y automatización de procesos empresariales. Tu tarea es generar el código completo y funcional de un chatbot de Telegram en Python que automatice el proceso de **solicitud y gestión de vacaciones** para la empresa "Active Dry S.A.", una PyME textil de 50 empleados.

El proyecto debe cumplir los requisitos del Trabajo Práctico Integrador de la materia Organización Empresarial de la Tecnicatura Universitaria en Programación a Distancia (UTN), modelando el flujo con lógica BPMN 2.0 traducida a código.

---

## DESCRIPCIÓN DEL PROCESO DE NEGOCIO (BPMN AS-IS → TO-BE)

### Proceso a automatizar: Solicitud de Vacaciones

**Actores:**
- **Empleado** (Usuario de Telegram): Inicia y responde en el chat.
- **Sistema/Bot**: Valida, consulta la base de datos y toma decisiones automáticas.
- **Director/Supervisor**: Recibe notificación y aprueba o rechaza (simulado en el bot con un comando de administrador).

**Flujo principal (Happy Path):**
1. Empleado inicia conversación → Bot saluda y pide número de legajo.
2. Empleado ingresa legajo → Bot valida que exista en la base de datos.
3. Bot muestra nombre del empleado y días disponibles → Pide fecha de inicio.
4. Empleado ingresa fecha de inicio (DD/MM/AAAA) → Bot valida formato y que sea futura.
5. Bot pide fecha de fin → Empleado ingresa fecha de fin (DD/MM/AAAA).
6. Bot calcula días hábiles solicitados → Valida que no supere el saldo disponible.
7. Bot verifica restricción operativa: no más del 50% del sector ausente simultáneamente.
8. Si todo OK → Bot registra solicitud como PENDIENTE y notifica al director simulado.
9. Director aprueba o rechaza mediante comando → Bot descuenta días y notifica al empleado.

**Caminos alternativos (Unhappy Path):**
- Legajo inexistente → Mensaje de error + reintento (máximo 3 intentos).
- Formato de fecha inválido → Mensaje de error + reintento.
- Fecha de inicio en el pasado → Rechazo con explicación.
- Días solicitados > saldo disponible → Rechazo con saldo actual mostrado.
- Conflicto operativo (>50% sector ausente) → Rechazo con fechas alternativas sugeridas.
- Empleado ya tiene solicitud PENDIENTE → Aviso y bloqueo de nueva solicitud.

---

## ESTRUCTURA DE ARCHIVOS A GENERAR

Genera todos los archivos con sus contenidos completos, en este orden:

```
chatbot_vacaciones/
├── bot.py                  # Archivo principal del bot
├── database.py             # Capa de acceso a datos (CSV + JSON)
├── states.py               # Máquina de estados (FSM)
├── validators.py           # Validaciones de negocio
├── handlers/
│   ├── __init__.py
│   ├── employee_handlers.py  # Flujo del empleado
│   └── admin_handlers.py     # Comandos de aprobación/rechazo
├── data/
│   ├── legajo.csv          # Base de datos de empleados
│   └── solicitudes.json    # Registro de solicitudes (se crea en runtime)
├── requirements.txt
└── README.md
```

---

## ESPECIFICACIONES TÉCNICAS DETALLADAS

### 1. Stack tecnológico
- **Lenguaje:** Python 3.10+
- **Librería principal:** `python-telegram-bot==20.x` (versión asíncrona con `ConversationHandler`)
- **Manejo de estados:** `ConversationHandler` de PTB con estados enumerados en `states.py`
- **Base de datos:** Archivo `legajo.csv` (lectura) + `solicitudes.json` (lectura/escritura)
- **Dependencias:** `python-telegram-bot`, `python-dotenv`, `pandas`

### 2. Archivo `legajo.csv` (contenido exacto a usar)

```csv
Legajo,Nombre del empleado,Días de vacaciones disponibles,Sector
001,Ricardo Fernández (Director),28,Dirección
002,Laura Méndez (Subdirectora),28,Dirección
003,Martín Salas (Jefe de Diseño),21,Diseño
004,Camila Torres,14,Diseño
005,Nicolás Vega,14,Diseño
006,Julieta Ríos,21,Diseño
007,Tomás Herrera,14,Diseño
008,Sergio Molina (Jefe de Producción),28,Producción
009,Carla Benítez,21,Producción
010,Emanuel Castro,14,Producción
011,Paula Giménez,14,Producción
012,Diego Acosta,21,Producción
013,Florencia Navarro,14,Producción
014,Gustavo Peralta,21,Producción
015,Micaela Suárez,14,Producción
016,Luciano Cabrera,14,Producción
017,Valeria Sosa,21,Producción
018,Andrés Paredes,14,Producción
019,Rocío Medina,14,Producción
020,Sebastián Quiroga,21,Producción
021,Daniela Ibarra,14,Ventas
022,Federico Luna,14,Ventas
023,Natalia Campos,21,Ventas
024,Javier Funes,14,Ventas
025,Belén Ortiz,14,Ventas
026,Mariano Delgado,21,Ventas
027,Sofía Ramírez,14,Ventas
028,Cristian Aguirre,14,Ventas
029,Verónica Silva,21,Ventas
030,Alan Pereyra,14,Ventas
031,Cecilia Roldán,14,Ventas
032,Hugo Benítez,21,Ventas
033,Melina Ferreyra,14,Ventas
034,Pablo Villalba,14,Ventas
035,Yanina Toledo,21,Ventas
036,Iván Correa,14,Ventas
037,Sandra Lucero,14,Ventas
038,Gabriel Núñez,21,Ventas
039,Romina Farías (Jefe de Ventas),21,Ventas
040,Leandro Paz,14,Ventas
041,Milagros Arias,14,Ventas
042,Kevin Domínguez,21,Administración
043,Agustina Bravo,14,Administración
044,Franco Leiva,14,Administración
045,Noelia Cejas,21,Administración
046,Esteban Riquelme,14,Administración
047,Patricia Godoy (Jefa Contable),28,Administración
048,Bruno Méndez,14,Administración
049,Karen Lozano,14,Administración
050,Rodrigo Escobar,14,Administración
```

### 3. Reglas de negocio a implementar

```python
# En validators.py implementar estas reglas:

# REGLA 1: Saldo de días según antigüedad (reflejado en CSV)
# - Hasta 5 años   → 14 días
# - 5 a 10 años    → 21 días
# - 10 a 20 años   → 28 días
# - Más de 20 años → 35 días

# REGLA 2: Restricción operativa por sector
# No puede estar ausente más del 50% de un mismo sector simultáneamente.
# Calcular empleados del sector y comparar con ausencias en el rango de fechas.

# REGLA 3: Días corridos (no hábiles) para el cálculo del consumo.
# Usar (fecha_fin - fecha_inicio).days + 1

# REGLA 4: Fecha de inicio debe ser al menos 5 días hábiles en el futuro
# (simular pre-aviso mínimo).

# REGLA 5: Máximo 1 solicitud PENDIENTE por empleado al mismo tiempo.
```

### 4. Máquina de estados (states.py)

```python
# Definir estos estados como IntEnum o constantes:
LEGAJO          = 0   # Esperando número de legajo
FECHA_INICIO    = 1   # Esperando fecha de inicio
FECHA_FIN       = 2   # Esperando fecha de fin
CONFIRMACION    = 3   # Mostrando resumen y pidiendo confirmación (sí/no)
FIN             = 4   # Conversación terminada
```

### 5. Estructura del archivo `solicitudes.json`

```json
{
  "solicitudes": [
    {
      "id": "SOL-001",
      "legajo": "025",
      "nombre": "Belén Ortiz",
      "sector": "Ventas",
      "fecha_inicio": "2026-07-10",
      "fecha_fin": "2026-07-20",
      "dias_solicitados": 11,
      "estado": "PENDIENTE",
      "telegram_chat_id": 123456789,
      "fecha_solicitud": "2026-06-01T10:30:00"
    }
  ]
}
```

### 6. Comandos del bot a implementar

**Para empleados:**
- `/start` → Inicia el flujo de solicitud de vacaciones.
- `/cancelar` → Cancela la conversación en cualquier punto.
- `/estado` → Consulta el estado de la última solicitud del empleado.
- `/saldo` → Consulta días disponibles (pide legajo).
- `/ayuda` → Muestra lista de comandos con descripción.

**Para administradores (ADMIN_CHAT_ID en .env):**
- `/aprobar SOL-001` → Aprueba la solicitud, descuenta días del CSV y notifica al empleado.
- `/rechazar SOL-001 [motivo]` → Rechaza la solicitud con motivo y notifica al empleado.
- `/pendientes` → Lista todas las solicitudes en estado PENDIENTE.
- `/historial [legajo]` → Muestra historial de solicitudes de un empleado.

### 7. Archivo `.env` (generar también `.env.example`)

```env
BOT_TOKEN=TU_TOKEN_AQUI
ADMIN_CHAT_ID=TU_CHAT_ID_AQUI
```

### 8. Mensajes del bot (tono corporativo pero amigable)

Todos los mensajes deben usar emojis apropiados y Markdown de Telegram:

```
Inicio:
"👋 ¡Bienvenido/a al Sistema de Gestión de Vacaciones de *Active Dry S.A.*!
Para comenzar, por favor ingresá tu *número de legajo* (ej: 025):"

Legajo válido:
"✅ Empleado/a encontrado/a:
👤 *Nombre:* {nombre}
🏢 *Sector:* {sector}
📅 *Días disponibles:* {dias} días

Ingresá la *fecha de inicio* de tus vacaciones (formato DD/MM/AAAA):"

Error legajo:
"❌ Legajo no encontrado. Por favor verificá el número e intentá nuevamente.
Intentos restantes: {n}"

Aprobación exitosa (al empleado):
"🎉 ¡Buenas noticias! Tu solicitud *SOL-XXX* fue *APROBADA*.
📅 Período: {fecha_inicio} al {fecha_fin}
📉 Días restantes: {saldo_nuevo} días
¡Que disfrutes tus vacaciones! 🏖️"

Rechazo:
"😔 Tu solicitud *SOL-XXX* fue *RECHAZADA*.
📝 Motivo: {motivo}
Para más información, contactá a Recursos Humanos."
```

---

## INSTRUCCIONES ESPECÍFICAS PARA GEMINI

1. **Genera cada archivo completo**, no uses `# ... resto del código`. Todo el código debe ser funcional y ejecutable.

2. **En `bot.py`**: Usa `ApplicationBuilder` de `python-telegram-bot` v20. El `ConversationHandler` debe cubrir todos los estados definidos. Configura `fallbacks` con `/cancelar` y mensajes de texto inesperados.

3. **En `database.py`**: Implementa funciones puras (sin efectos secundarios excepto escritura a JSON):
   - `buscar_empleado(legajo: str) -> dict | None`
   - `obtener_empleados_sector(sector: str) -> list[dict]`
   - `guardar_solicitud(solicitud: dict) -> str` (retorna ID generado)
   - `actualizar_estado_solicitud(id_sol: str, nuevo_estado: str, motivo: str = "") -> bool`
   - `descontar_dias(legajo: str, dias: int) -> bool`
   - `obtener_solicitudes_pendientes() -> list[dict]`
   - `obtener_solicitud_por_id(id_sol: str) -> dict | None`
   - `hay_solicitud_pendiente(legajo: str) -> bool`

4. **En `validators.py`**: Implementa:
   - `validar_formato_fecha(texto: str) -> date | None`
   - `validar_fecha_futura(fecha: date, dias_minimos: int = 5) -> bool`
   - `calcular_dias_solicitados(inicio: date, fin: date) -> int`
   - `validar_saldo(legajo: str, dias: int) -> tuple[bool, int]` (retorna (válido, saldo_actual))
   - `verificar_restriccion_sector(sector: str, inicio: date, fin: date) -> tuple[bool, str]`

5. **Manejo de errores robusto**: Cada handler debe tener try/except. Si algo falla inesperadamente, el bot responde con un mensaje amigable y loggea el error.

6. **Logging**: Configura `logging` básico al inicio de `bot.py` con nivel INFO, mostrando timestamp, nivel y mensaje.

7. **El `README.md`** debe incluir:
   - Descripción del proyecto
   - Requisitos previos
   - Instrucciones de instalación (paso a paso)
   - Cómo obtener el token de Telegram
   - Cómo ejecutar el bot
   - Lista de comandos disponibles
   - Estructura del proyecto
   - Ejemplo de sesión de conversación

8. **Comentarios en el código**: Cada función debe tener docstring. Las secciones de lógica de negocio deben tener comentarios explicando la regla BPMN que implementan (ej: `# GATEWAY: ¿Tiene saldo suficiente?`).

---

## EJEMPLO DE SESIÓN ESPERADA (para referencia)

```
Usuario: /start
Bot: 👋 ¡Bienvenido/a al Sistema de Gestión de Vacaciones de Active Dry S.A.!
     Para comenzar, ingresá tu número de legajo (ej: 025):

Usuario: 025
Bot: ✅ Empleado/a encontrado/a:
     👤 Nombre: Belén Ortiz
     🏢 Sector: Ventas
     📅 Días disponibles: 14 días
     
     Ingresá la fecha de inicio de tus vacaciones (formato DD/MM/AAAA):

Usuario: 10/07/2026
Bot: 📅 Fecha de inicio: 10/07/2026 ✓
     Ahora ingresá la fecha de fin (DD/MM/AAAA):

Usuario: 20/07/2026
Bot: 📋 Resumen de tu solicitud:
     👤 Empleado: Belén Ortiz
     🏢 Sector: Ventas
     📅 Desde: 10/07/2026
     📅 Hasta: 20/07/2026
     📊 Días solicitados: 11
     💼 Días disponibles: 14
     
     ¿Confirmás la solicitud? Respondé SI o NO:

Usuario: SI
Bot: ✅ Solicitud registrada con ID: SOL-001
     Está siendo revisada por tu supervisor. Te notificaremos cuando sea procesada.

[Admin recibe notificación]
Admin: /aprobar SOL-001
Bot (al admin): ✅ Solicitud SOL-001 aprobada correctamente.
Bot (al empleado): 🎉 ¡Tu solicitud SOL-001 fue APROBADA! ...
```

---

## RESTRICCIONES Y ACLARACIONES

- **No uses librerías de terceros** más allá de las listadas en `requirements.txt`.
- El CSV de legajos se lee al inicio y se mantiene en memoria (dict cacheado). Las escrituras van al CSV.
- El JSON de solicitudes se lee y escribe en disco en cada operación (para simular persistencia real).
- No implementes base de datos SQL; el enunciado del TP permite plantillas/CSV como persistencia.
- El bot debe funcionar con un solo proceso (no usar webhooks, solo polling).
- Estructura el código para que sea fácil de extender (agregar nuevos handlers o reglas).

---

## ENTREGABLE ESPERADO

Un bloque de código por cada archivo, claramente delimitado con el nombre del archivo como título, listo para copiar y pegar en los archivos correspondientes del proyecto.
