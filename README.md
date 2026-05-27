# Chatbot de Gestión de Vacaciones - Active Dry S.A. 🏖️

Este proyecto consiste en un chatbot de Telegram desarrollado en Python para automatizar el proceso de solicitud y gestión de vacaciones de la empresa **Active Dry S.A.**

El sistema utiliza una máquina de estados (FSM) para guiar a los empleados en sus solicitudes, validando automáticamente las reglas de negocio antes de enviarlas al panel de administración para su aprobación o rechazo.

## 🚀 Requisitos Previos

- Python 3.10 o superior.
- Una cuenta de Telegram y un bot creado vía [@BotFather](https://t.me/botfather).
- ID de chat de Telegram del administrador (puedes obtenerlo usando [@userinfobot](https://t.me/userinfobot)).

## 📦 Instalación y Configuración

1. **Clonar el proyecto:**
   ```bash
   git clone <url-del-repositorio>
   cd chatbot_vacaciones
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo `.env` basado en `.env.example`:
   ```env
   BOT_TOKEN=tu_token_de_telegram
   ADMIN_CHAT_ID=tu_id_de_chat
   ```

## 🏃 Ejecución

Para iniciar el bot:
```bash
python bot.py
```

## 🛠️ Comandos Disponibles

### Para Empleados
- `/start`: Inicia el flujo guiado para solicitar vacaciones.
- `/estado [legajo]`: Consulta el estado de tu última solicitud.
- `/saldo [legajo]`: Consulta tus días de vacaciones disponibles.
- `/cancelar`: Cancela cualquier proceso en curso.
- `/ayuda`: Muestra la lista de comandos disponibles.

### Para Administradores (Requiere ID configurado)
- `/pendientes`: Lista las solicitudes que esperan revisión.
- `/aprobar [ID_SOL]`: Aprueba una solicitud y descuenta los días del legajo.
- `/rechazar [ID_SOL] [motivo]`: Rechaza la solicitud con un motivo opcional.
- `/historial [legajo]`: Ver todas las solicitudes (pasadas y presentes) de un empleado.

## 📋 Reglas de Negocio (Automatizadas)

1. **Pre-aviso Mínimo:** Las solicitudes deben realizarse con al menos **5 días de anticipación** a la fecha de inicio.
2. **Saldo de Vacaciones:** No se pueden solicitar más días de los que el empleado tiene disponibles en `legajo.csv`.
3. **Continuidad Operativa (Sector):** No puede estar ausente más del **50% de un mismo sector** simultáneamente.
4. **Restricción de Jerarquía:** El Director y la Subdirectora no pueden tomar vacaciones en el mismo período.
5. **Solicitud Única:** Un empleado solo puede tener **una solicitud en estado PENDIENTE** a la vez.
6. **Cálculo de Días:** Se consideran **días corridos** (incluyendo fines de semana) entre la fecha de inicio y fin.

## 📂 Estructura del Proyecto

- `bot.py`: Punto de entrada y configuración de la aplicación.
- `database.py`: Manejo de persistencia de datos (CSV y JSON).
- `validators.py`: Lógica de validación de reglas de negocio.
- `states.py`: Definición de estados para la conversación (FSM).
- `handlers/`: Módulos con la lógica de respuesta para empleados y admins.
- `data/`: Directorio que contiene los archivos de datos (`legajo.csv` y `solicitudes.json`).

---
*Desarrollado para la materia Organización Empresarial - UTN TUPaD.*
