import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from PIL import Image
import io

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

def apply_antialiasing_filter(image):
    """Применяет фильтр для удаления одиночных пикселей"""
    pixels = image.load()
    width, height = image.size
    
    # Создаем копию для изменений
    filtered_image = image.copy()
    filtered_pixels = filtered_image.load()
    
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            current_pixel = pixels[x, y]
            
            # Считаем черные пиксели в окрестности 3x3
            black_neighbors = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if pixels[nx, ny] == 0:  # Черный пиксель
                            black_neighbors += 1
            
            # Убираем одиночные черные пиксели (менее 2 соседей)
            if current_pixel == 0 and black_neighbors < 2:
                filtered_pixels[x, y] = 255  # Белый
            # Убираем одиночные белые пиксели в черной области
            elif current_pixel == 255 and black_neighbors > 6:
                filtered_pixels[x, y] = 0  # Черный
    
    return filtered_image

def image_to_hex_array(image):
    """Конвертирует изображение в HEX массив для ESP32"""
    # ... существующий код ...

def image_to_hex_array(image):
    """Конвертирует изображение в HEX массив для ESP32"""
    pixels = list(image.getdata())
    width, height = image.size
    
    hex_array = []
    for y in range(0, height, 8):
        for x in range(width):
            byte = 0
            for bit in range(8):
                if y + bit < height:
                    pixel = pixels[(y + bit) * width + x]
                    if pixel == 0:  # Чёрный пиксель
                        byte |= (1 << bit)
            hex_array.append(f"0x{byte:02X}")
    
    return "{" + ", ".join(hex_array) + "}"

async def handle_image(update: Update, context: CallbackContext) -> None:
    """Обработчик загрузки изображений с конвертацией в битмап"""
    try:
        # Получаем файл изображения
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Конвертируем изображение
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Преобразуем в монохром 128x64
        image = image.convert('1')  # Монохром (чёрно-белое)
        image = image.resize((128, 64))
        
        # Сохраняем превью
        preview_bytes = io.BytesIO()
        image.save(preview_bytes, 'PNG')
        preview_bytes.seek(0)
        
        # Генерируем HEX массив для ESP32
        hex_array = image_to_hex_array(image)
        
        # Отправляем результат
        await update.message.reply_photo(
            photo=preview_bytes,
            caption="✅ Вот как это будет выглядеть на OLED дисплее!\n\n"
                   "Скопируй этот массив в код ESP32:\n\n"
                   f"`{hex_array[:100]}...`"
        )
        
        # Отправляем полный массив отдельными частями
        max_length = 4000  # Максимальная длина сообщения в Telegram
        for i in range(0, len(hex_array), max_length):
            chunk = hex_array[i:i + max_length]
            await update.message.reply_text(f"`{chunk}`", parse_mode='MarkdownV2')
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

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
