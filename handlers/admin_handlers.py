from telegram import Update
from telegram.ext import ContextTypes
import database
import os
import logging

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

def is_admin(update: Update):
    """Verifica si el usuario es el administrador."""
    return str(update.effective_chat.id) == str(ADMIN_CHAT_ID)

async def aprobar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /aprobar ID_SOL"""
    if not is_admin(update):
        return

    if not context.args:
        await update.message.reply_text("Uso: /aprobar SOL-XXX")
        return

    id_sol = context.args[0].upper()
    solicitud = database.obtener_solicitud_por_id(id_sol)

    if not solicitud:
        await update.message.reply_text("❌ Solicitud no encontrada.")
        return

    if solicitud["estado"] != "PENDIENTE":
        await update.message.reply_text(f"❌ La solicitud ya está en estado {solicitud['estado']}.")
        return

    # Acción de aprobación
    if database.actualizar_estado_solicitud(id_sol, "APROBADA"):
        database.descontar_dias(solicitud["legajo"], solicitud["dias_solicitados"])
        
        # Notificar al admin
        await update.message.reply_text(f"✅ Solicitud {id_sol} aprobada correctamente.")
        
        # Notificar al empleado
        try:
            nuevo_saldo = database.buscar_empleado(solicitud["legajo"])["Días de vacaciones disponibles"]
            await context.bot.send_message(
                chat_id=solicitud["telegram_chat_id"],
                text=f"🎉 ¡Buenas noticias! Tu solicitud *{id_sol}* fue *APROBADA*.\n"
                     f"📅 Período: {solicitud['fecha_inicio']} al {solicitud['fecha_fin']}\n"
                     f"📉 Días restantes: {nuevo_saldo} días\n"
                     "¡Que disfrutes tus vacaciones! 🏖️",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error notificando al empleado: {e}")
    else:
        await update.message.reply_text("❌ Error al procesar la aprobación.")

async def rechazar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /rechazar ID_SOL [motivo]"""
    if not is_admin(update):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Uso: /rechazar SOL-XXX [motivo]")
        return

    id_sol = context.args[0].upper()
    motivo = " ".join(context.args[1:]) if len(context.args) > 1 else "No especificado"
    
    solicitud = database.obtener_solicitud_por_id(id_sol)

    if not solicitud:
        await update.message.reply_text("❌ Solicitud no encontrada.")
        return

    if solicitud["estado"] != "PENDIENTE":
        await update.message.reply_text(f"❌ La solicitud ya está en estado {solicitud['estado']}.")
        return

    if database.actualizar_estado_solicitud(id_sol, "RECHAZADA", motivo):
        await update.message.reply_text(f"✅ Solicitud {id_sol} rechazada.")
        
        # Notificar al empleado
        try:
            await context.bot.send_message(
                chat_id=solicitud["telegram_chat_id"],
                text=f"😔 Tu solicitud *{id_sol}* fue *RECHAZADA*.\n"
                     f"📝 Motivo: {motivo}\n"
                     "Para más información, contactá a Recursos Humanos.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error notificando al empleado: {e}")
    else:
        await update.message.reply_text("❌ Error al procesar el rechazo.")

async def listar_pendientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /pendientes"""
    if not is_admin(update):
        return

    pendientes = database.obtener_solicitudes_pendientes()
    if not pendientes:
        await update.message.reply_text("No hay solicitudes pendientes.")
        return

    mensaje = "📋 *Solicitudes Pendientes:*\n\n"
    for s in pendientes:
        mensaje += f"🆔 {s['id']} - {s['nombre']} ({s['sector']})\n"
        mensaje += f"📅 {s['fecha_inicio']} al {s['fecha_fin']} ({s['dias_solicitados']} días)\n\n"
    
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def historial_empleado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /historial [legajo]"""
    if not is_admin(update):
        return

    if not context.args:
        await update.message.reply_text("Uso: /historial [legajo]")
        return

    legajo = context.args[0]
    historial = database.obtener_historial_empleado(legajo)
    
    if not historial:
        await update.message.reply_text(f"No hay historial para el legajo {legajo}.")
        return

    mensaje = f"📜 *Historial de solicitudes (Legajo {legajo}):*\n\n"
    for s in historial:
        mensaje += f"🆔 {s['id']} - {s['estado']}\n"
        mensaje += f"📅 {s['fecha_inicio']} al {s['fecha_fin']}\n"
        if s.get("motivo_rechazo"):
            mensaje += f"📝 Motivo: {s['motivo_rechazo']}\n"
        mensaje += "---\n"
    
    await update.message.reply_text(mensaje, parse_mode="Markdown")
