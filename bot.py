import os
import django
import logging

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_report.settings')
django.setup()

from django.conf import settings
from telegram.ext import Application, ConversationHandler, MessageHandler, filters, CommandHandler

from handlers import Handlers, SELECTING_CHAIN, SELECTING_CATEGORY, SELECTING_BRAND, UPLOADING_PHOTOS, COMPETITOR_MODE


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class PharmacyBot:
    def __init__(self):
        self.token = settings.BOT_TOKEN
        self.application = Application.builder().token(self.token).build()
        self.handlers = Handlers()
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка всех обработчиков команд"""

        # Обработчик для команды "Завершить отчет" из любого состояния
        cancel_command = CommandHandler('cancel', self.handlers.cancel)
        finish_text = MessageHandler(filters.Regex(r'^Завершить.*отчет$'), self.handlers.handle_finish_anywhere)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('new_report', self.handlers.new_report)],
            states={
                SELECTING_CHAIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.select_chain),
                    finish_text  # Можно завершить даже на этапе выбора сети
                ],
                SELECTING_CATEGORY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.select_category),
                    finish_text  # Можно завершить на этапе выбора категории
                ],
                SELECTING_BRAND: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.select_brand),
                    finish_text  # Можно завершить на этапе выбора бренда
                ],
                UPLOADING_PHOTOS: [
                    MessageHandler(filters.PHOTO, self.handlers.handle_photo),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_text),
                    finish_text  # Можно завершить при загрузке фото
                ],
                COMPETITOR_MODE: [
                    MessageHandler(filters.PHOTO, self.handlers.handle_competitor_photo),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_competitor_text),
                    finish_text  # Можно завершить в режиме конкурентов
                ]
            },
            fallbacks=[cancel_command, finish_text]  # Двойной fallback
        )

        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(conv_handler)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.unknown_command)
        )

    def run(self):
        """Запуск бота"""
        self.application.run_polling()


if __name__ == "__main__":
    bot = PharmacyBot()
    print("Бот запущен...")
    bot.run()
