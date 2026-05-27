# 🏖️ Manual de Usuario - Chatbot de Vacaciones (Active Dry S.A.)

Este manual describe el funcionamiento y uso del chatbot de Telegram diseñado para la gestión de solicitudes de vacaciones de **Active Dry S.A.**

---

## 🚀 1. Configuración Inicial

Para que el sistema funcione correctamente, se deben seguir estos pasos:

1. **Requisitos:** Tener instalado Python 3.10+ y las librerías necesarias (`pip install -r requirements.txt`).
2. **Variables de Entorno:** Configurar el archivo `.env` con:
   - `BOT_TOKEN`: Token obtenido de [@BotFather](https://t.me/botfather).
   - `ADMIN_CHAT_ID`: El ID de chat de Telegram del administrador (puedes obtenerlo enviando un mensaje a [@userinfobot](https://t.me/userinfobot)).
3. **Datos:** Asegurarse de que el archivo `data/legajo.csv` contenga la lista actualizada de empleados y sus días disponibles.
4. **Ejecución:** Iniciar el bot con el comando:
   ```bash
   python bot.py
   ```

---

## 👥 2. Guía para Empleados

El bot permite a los empleados solicitar vacaciones, consultar su saldo y ver el estado de sus solicitudes.

### 📝 Cómo realizar una solicitud
1. Iniciá el chat con el comando `/start`.
2. Ingresá tu **número de legajo** (ej: `025`). El sistema validará tu identidad.
3. Ingresá la **fecha de inicio** (formato `DD/MM/AAAA`).
   - *Nota:* Debe tener al menos 5 días de anticipación.
4. Ingresá la **fecha de fin** (formato `DD/MM/AAAA`).
5. El bot mostrará un **resumen**. Si los datos son correctos, confirmá escribiendo **SI**.
6. Recibirás un ID de solicitud (ej: `SOL-001`) y el administrador será notificado.

### 🔍 Otros comandos útiles
- `/saldo [legajo]`: Consultá cuántos días de vacaciones tenés disponibles.
- `/estado [legajo]`: Consultá el estado (Pendiente, Aprobada o Rechazada) de tu última solicitud.
- `/ayuda`: Mostrá la lista de comandos disponibles.
- `/cancelar`: Cancelá el proceso de solicitud en cualquier momento.

---

## ⚡ 3. Guía para Administradores (RRHH / Supervisores)

Los administradores tienen acceso a comandos exclusivos para gestionar las solicitudes. Estos comandos solo funcionan si se envían desde el chat configurado en `ADMIN_CHAT_ID`.

### 📋 Gestión de solicitudes
- `/pendientes`: Listá todas las solicitudes que esperan revisión.
- `/aprobar [ID_SOL]`: Aprobá una solicitud (ej: `/aprobar SOL-001`). 
  - Al aprobar, el empleado es notificado y se descuentan automáticamente los días de su `legajo.csv`.
- `/rechazar [ID_SOL] [motivo]`: Rechazá una solicitud indicando la razón (ej: `/rechazar SOL-001 No hay cobertura en el sector`).
  - El empleado recibirá una notificación con el motivo del rechazo.
- `/historial [legajo]`: Consultá todas las solicitudes pasadas de un empleado específico.

---

## 📏 4. Reglas de Negocio

Para asegurar el correcto funcionamiento de la empresa, el bot aplica las siguientes validaciones automáticas:

1. **Pre-aviso:** Las solicitudes deben hacerse con un mínimo de **5 días de anticipación**.
2. **Saldo Insuficiente:** No se permiten solicitudes que excedan los días disponibles del empleado.
3. **Restricción de Sector:** El sistema impide que más del **50% de los empleados de un mismo sector** estén de vacaciones simultáneamente.
4. **Restricción Jerárquica:** Dos directivos del mismo rango no pueden ausentarse al mismo tiempo.
5. **Solicitud Única:** Un empleado no puede realizar una nueva solicitud si ya tiene una en estado **PENDIENTE**.
6. **Días Corridos:** El cálculo de días incluye fines de semana y feriados.

---

## 🛠️ 5. Soporte Técnico

En caso de errores o dudas:
- Verificá que el bot esté en ejecución en el servidor.
- Revisá el archivo `data/solicitudes.json` para auditorías manuales.
- Contactá al administrador del sistema si tu legajo no es reconocido.
