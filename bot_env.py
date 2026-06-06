import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import mss
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Cargar variables de entorno (opcional)
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tu token de bot de Telegram
# Puede venir de:
# 1. Variable de entorno TELEGRAM_TOKEN en .env
# 2. Configurado directamente abajo
TOKEN = os.getenv('TELEGRAM_TOKEN', 'TU_TOKEN_AQUI')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida"""
    await update.message.reply_text(
        "¡Hola! Soy tu bot de captura de pantalla.\n\n"
        "Comandos disponibles:\n"
        "/screenshot - Toma una captura de pantalla\n"
        "/help - Muestra esta ayuda"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help - Muestra los comandos disponibles"""
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/screenshot - Toma una captura de pantalla de tu PC\n"
        "/start - Muestra el mensaje de bienvenida\n"
        "/help - Muestra esta ayuda"
    )

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /screenshot - Toma una captura de pantalla y la envía"""
    try:
        # Mostrar que se está procesando
        await update.message.reply_text("📸 Tomando captura de pantalla...")
        
        # Capturar la pantalla
        with mss.mss() as sct:
            # Capturar el monitor principal (índice 1)
            monitor = sct.monitors[1]
            screenshot_data = sct.grab(monitor)
            
            # Convertir a imagen PIL
            img = Image.frombytes('RGB', screenshot_data.size, screenshot_data.rgb)
            
            # Guardar en buffer
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Enviar la imagen
            await update.message.reply_photo(
                photo=buffer,
                caption="📸 Captura de pantalla de tu PC"
            )
            
            logger.info(f"Captura enviada a {update.effective_user.first_name}")
            
    except Exception as e:
        logger.error(f"Error al tomar captura: {e}")
        await update.message.reply_text(f"❌ Error al tomar captura: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores"""
    logger.error(f"Update {update} causó error {context.error}")

def main() -> None:
    """Inicia el bot"""
    
    # Verificar que el token está configurado
    if TOKEN == "TU_TOKEN_AQUI":
        logger.error("❌ ERROR: Debes configurar tu TOKEN de Telegram")
        print("\n" + "="*60)
        print("IMPORTANTE: Debes obtener tu token de Telegram")
        print("1. Abre Telegram")
        print("2. Busca a @BotFather")
        print("3. Envía /newbot")
        print("4. Sigue las instrucciones")
        print("5. Copia el token en bot_env.py o en el archivo .env")
        print("="*60 + "\n")
        return
    
    # Crear la aplicación
    application = Application.builder().token(TOKEN).build()
    
    # Agregar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("screenshot", screenshot))
    
    # Agregar handler de errores
    application.add_error_handler(error_handler)
    
    # Iniciar el bot
    logger.info("🤖 Bot iniciado. Presiona Ctrl+C para detener.")
    print("\n✅ Bot ejecutándose correctamente. Puedes enviar comandos desde Telegram.\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
