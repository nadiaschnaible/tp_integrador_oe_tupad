import logging
import os
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

# Cargar variables de entorno
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Configuración de Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from states import State
from handlers import employee_handlers, admin_handlers

def main():
    """Configura e inicia el bot."""
    if not BOT_TOKEN:
        logging.error("No se encontró el BOT_TOKEN en el archivo .env")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation Handler para el flujo de solicitud del empleado
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", employee_handlers.start)],
        states={
            State.LEGAJO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, employee_handlers.handle_legajo)
            ],
            State.FECHA_INICIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, employee_handlers.handle_fecha_inicio)
            ],
            State.FECHA_FIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, employee_handlers.handle_fecha_fin)
            ],
            State.CONFIRMACION: [
                MessageHandler(filters.Regex("^(SI|NO|Si|No|si|no)$"), employee_handlers.handle_confirmacion)
            ],
        },
        fallbacks=[CommandHandler("cancelar", employee_handlers.cancel)],
    )

    # Agregar Handlers de Empleado
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("estado", employee_handlers.estado_solicitud))
    application.add_handler(CommandHandler("saldo", employee_handlers.saldo_vacaciones))
    application.add_handler(CommandHandler("ayuda", employee_handlers.ayuda))
    application.add_handler(CommandHandler("cancelar", employee_handlers.cancel))

    # Agregar Handlers de Administrador
    application.add_handler(CommandHandler("aprobar", admin_handlers.aprobar_solicitud))
    application.add_handler(CommandHandler("rechazar", admin_handlers.rechazar_solicitud))
    application.add_handler(CommandHandler("pendientes", admin_handlers.listar_pendientes))
    application.add_handler(CommandHandler("historial", admin_handlers.historial_empleado))

    # Handler para mensajes no reconocidos (debe ir al final)
    application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, employee_handlers.mensaje_desconocido))

    # Inicio del bot
    logging.info("Bot iniciado...")
    application.run_polling()

if __name__ == "__main__":
    main()
