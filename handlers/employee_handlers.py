from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from states import State
import database
import validators
from datetime import date
import os
import logging

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia el flujo de solicitud de vacaciones."""
    await update.message.reply_text(
        "👋 ¡Bienvenido/a al Sistema de Gestión de Vacaciones de *Active Dry S.A.*!\n"
        "Para comenzar, por favor ingresá tu *número de legajo* (ej: 025):",
        parse_mode="Markdown"
    )
    context.user_data["intentos_legajo"] = 3
    return State.LEGAJO

async def handle_legajo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida el legajo del empleado."""
    legajo = update.message.text.strip()
    empleado = database.buscar_empleado(legajo)
    
    if empleado:
        if database.hay_solicitud_pendiente(legajo):
            await update.message.reply_text(
                "⚠️ Ya tenés una solicitud *PENDIENTE*. No podés realizar una nueva hasta que la anterior sea procesada.",
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        
        context.user_data["empleado"] = empleado
        await update.message.reply_text(
            f"✅ Empleado/a encontrado/a:\n"
            f"👤 *Nombre:* {empleado['Nombre del empleado']}\n"
            f"🏢 *Sector:* {empleado['Sector']}\n"
            f"📅 *Días disponibles:* {empleado['Días de vacaciones disponibles']} días\n\n"
            f"Ingresá la *fecha de inicio* de tus vacaciones (formato DD/MM/AAAA):",
            parse_mode="Markdown"
        )
        return State.FECHA_INICIO
    else:
        context.user_data["intentos_legajo"] -= 1
        intentos = context.user_data["intentos_legajo"]
        if intentos > 0:
            await update.message.reply_text(
                f"❌ Legajo no encontrado. Por favor verificá el número e intentá nuevamente.\n"
                f"Intentos restantes: {intentos}"
            )
            return State.LEGAJO
        else:
            await update.message.reply_text("❌ Se agotaron los intentos. Por favor, contactá a RRHH.")
            return ConversationHandler.END

async def handle_fecha_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida la fecha de inicio."""
    texto = update.message.text.strip()
    fecha_inicio = validators.validar_formato_fecha(texto)
    
    if not fecha_inicio:
        await update.message.reply_text("❌ Formato inválido. Usá DD/MM/AAAA (ej: 10/07/2026):")
        return State.FECHA_INICIO
    
    if not validators.validar_fecha_futura(fecha_inicio):
        await update.message.reply_text("❌ La fecha de inicio debe ser al menos 5 días hábiles en el futuro.")
        return State.FECHA_INICIO
    
    context.user_data["fecha_inicio"] = fecha_inicio
    await update.message.reply_text(
        f"📅 Fecha de inicio: {fecha_inicio.strftime('%d/%m/%Y')} ✓\n"
        "Ahora ingresá la *fecha de fin* (DD/MM/AAAA):",
        parse_mode="Markdown"
    )
    return State.FECHA_FIN

async def handle_fecha_fin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida la fecha de fin y muestra resumen."""
    texto = update.message.text.strip()
    fecha_fin = validators.validar_formato_fecha(texto)
    fecha_inicio = context.user_data["fecha_inicio"]
    empleado = context.user_data["empleado"]
    
    if not fecha_fin:
        await update.message.reply_text("❌ Formato inválido. Usá DD/MM/AAAA:")
        return State.FECHA_FIN
    
    if fecha_fin < fecha_inicio:
        await update.message.reply_text("❌ La fecha de fin no puede ser anterior a la de inicio. Ingresá nuevamente la fecha de fin:")
        return State.FECHA_FIN
    
    if not validators.validar_rango_razonable(fecha_inicio, fecha_fin):
        await update.message.reply_text(
            f"❌ El período solicitado es demasiado largo (máximo {validators.MAX_DIAS_VACACIONES} días). "
            "Por favor, ingresá una fecha de fin más cercana:"
        )
        return State.FECHA_FIN
    
    dias_solicitados = validators.calcular_dias_solicitados(fecha_inicio, fecha_fin)
    valido_saldo, saldo_actual = validators.validar_saldo(empleado["Legajo"], dias_solicitados)
    
    if not valido_saldo:
        await update.message.reply_text(
            f"❌ No tenés saldo suficiente. Solicitaste {dias_solicitados} días pero tenés {saldo_actual}."
        )
        return State.FECHA_FIN
    
    valido_sector, mensaje_error = validators.verificar_restriccion_sector(
        empleado["Sector"], fecha_inicio, fecha_fin
    )
    
    if not valido_sector:
        await update.message.reply_text(f"❌ {mensaje_error}\nPor favor, intentá con otras fechas.")
        return State.FECHA_INICIO

    valido_jerarquia, mensaje_jerarquia = validators.verificar_restriccion_jerarquia(
        empleado["Legajo"], fecha_inicio, fecha_fin
    )

    if not valido_jerarquia:
        await update.message.reply_text(f"❌ {mensaje_jerarquia}\nPor favor, coordiná con el otro directivo.")
        return State.FECHA_INICIO

    context.user_data["fecha_fin"] = fecha_fin
    context.user_data["dias_solicitados"] = dias_solicitados
    
    reply_keyboard = [["SI", "NO"]]
    await update.message.reply_text(
        "📋 *Resumen de tu solicitud:*\n"
        f"👤 *Empleado:* {empleado['Nombre del empleado']}\n"
        f"🏢 *Sector:* {empleado['Sector']}\n"
        f"📅 *Desde:* {fecha_inicio.strftime('%d/%m/%Y')}\n"
        f"📅 *Hasta:* {fecha_fin.strftime('%d/%m/%Y')}\n"
        f"📊 *Días solicitados:* {dias_solicitados}\n"
        f"💼 *Días disponibles:* {saldo_actual}\n\n"
        "¿Confirmás la solicitud? Respondé *SI* o *NO*:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return State.CONFIRMACION

async def handle_confirmacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la confirmación final."""
    respuesta = update.message.text.strip().upper()
    
    if respuesta == "SI":
        empleado = context.user_data["empleado"]
        solicitud = {
            "legajo": str(empleado["Legajo"]),
            "nombre": empleado["Nombre del empleado"],
            "sector": empleado["Sector"],
            "fecha_inicio": context.user_data["fecha_inicio"].isoformat(),
            "fecha_fin": context.user_data["fecha_fin"].isoformat(),
            "dias_solicitados": context.user_data["dias_solicitados"],
            "estado": "PENDIENTE",
            "telegram_chat_id": update.effective_chat.id
        }
        id_sol = database.guardar_solicitud(solicitud)
        
        await update.message.reply_text(
            f"✅ Solicitud registrada con ID: *{id_sol}*\n"
            "Está siendo revisada por tu supervisor. Te notificaremos cuando sea procesada.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Notificar al admin
        if ADMIN_CHAT_ID:
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"🔔 *Nueva solicitud de vacaciones*\n"
                         f"🆔 ID: {id_sol}\n"
                         f"👤 Empleado: {solicitud['nombre']}\n"
                         f"🏢 Sector: {solicitud['sector']}\n"
                         f"📅 Período: {context.user_data['fecha_inicio'].strftime('%d/%m/%Y')} al {context.user_data['fecha_fin'].strftime('%d/%m/%Y')}\n"
                         f"📊 Días: {solicitud['dias_solicitados']}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"Error notificando al admin: {e}")
                
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Solicitud cancelada.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversación."""
    await update.message.reply_text("Operación cancelada. ¡Hasta luego!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def estado_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta el estado de la última solicitud (requiere legajo en argumentos o guardado)."""
    if not context.args:
        await update.message.reply_text("Uso: /estado [tu_legajo]")
        return
    
    legajo = context.args[0]
    sol = database.obtener_ultima_solicitud(legajo)
    
    if not sol:
        await update.message.reply_text("No se encontraron solicitudes para ese legajo.")
        return
    
    await update.message.reply_text(
        f"📋 *Última solicitud:* {sol['id']}\n"
        f"📅 Período: {sol['fecha_inicio']} al {sol['fecha_fin']}\n"
        f"📊 Estado: *{sol['estado']}*",
        parse_mode="Markdown"
    )

async def saldo_vacaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta los días disponibles."""
    if not context.args:
        await update.message.reply_text("Uso: /saldo [tu_legajo]")
        return
    
    legajo = context.args[0]
    empleado = database.buscar_empleado(legajo)
    
    if not empleado:
        await update.message.reply_text("Legajo no encontrado.")
        return
    
    await update.message.reply_text(
        f"👤 *Empleado:* {empleado['Nombre del empleado']}\n"
        f"📅 *Días disponibles:* {empleado['Días de vacaciones disponibles']}",
        parse_mode="Markdown"
    )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la ayuda."""
    texto = (
        "📖 *Comandos disponibles:*\n\n"
        "/start - Iniciar solicitud de vacaciones\n"
        "/cancelar - Cancelar el flujo actual\n"
        "/estado [legajo] - Ver estado de tu última solicitud\n"
        "/saldo [legajo] - Consultar tus días disponibles\n"
        "/ayuda - Mostrar este mensaje"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

async def mensaje_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto o comandos no reconocidos fuera del flujo de conversación."""
    texto = (
        "🤖 *¡Hola! No reconocí ese mensaje o comando.*\n\n"
        "Soy el bot de gestión de vacaciones de *Active Dry S.A.*\n"
        "Para interactuar conmigo, usá los siguientes comandos:\n\n"
        "▶️ /start - Iniciar una nueva solicitud de vacaciones\n"
        "🔍 /estado [legajo] - Ver el estado de tu última solicitud\n"
        "📅 /saldo [legajo] - Consultar cuántos días tenés disponibles\n"
        "❓ /ayuda - Mostrar esta ayuda"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")
