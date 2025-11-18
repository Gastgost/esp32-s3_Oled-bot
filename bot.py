import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Твой токен бота
BOT_TOKEN = "8597269707:AAEp_kd2MD8rhRNQxRV16WDY--EnVQCTQpI"

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🖼️ Привет! Я бот для конвертации изображений в битмапы для ESP32 OLED дисплея!\n\n"
        "Просто отправь мне картинку, и я преобразую её в монохромный формат 128x64 пикселей!"
    )

async def handle_image(update: Update, context: CallbackContext) -> None:
    """Обработчик загрузки изображений"""
    await update.message.reply_text("📸 Картинка получена! Функция конвертации скоро будет добавлена!")

def main() -> None:
    """Запуск бота"""
    logger.info("Запуск бота...")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    # Запускаем бота
    logger.info("Бот запущен и работает!")
    application.run_polling()

if __name__ == "__main__":
    main()
