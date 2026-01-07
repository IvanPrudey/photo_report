import os
import django
import logging
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_report.settings')
django.setup()

from django.core.files.base import ContentFile
from django.conf import settings
from asgiref.sync import sync_to_async
from reports.models import User, TradingClient, CategoryProduct, BrandProduct, PhotoReport

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

logger = logging.getLogger(__name__)

SELECTING_CHAIN, SELECTING_CATEGORY, SELECTING_BRAND, UPLOADING_PHOTOS, COMPETITOR_MODE = range(5)


class Handlers:
    def __init__(self):
        pass

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        keyboard = [["📋 Новый отчет"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        db_user, created = await sync_to_async(User.objects.get_or_create)(
            telegram_id=user.id,
            defaults={
                'username': user.username or f"user_{user.id}",
                'first_name': user.first_name or '',
                'last_name': user.last_name or ''
            }
        )
        await sync_to_async(db_user.update_activity)()
        welcome_text = (
            f"Добро пожаловать, {user.first_name}!\n\n"
            "Я бот для создания фотоотчетов по мерчандайзингу.\n"
            "Нажмите кнопку ниже для создания нового отчета"
        )
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def new_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания нового отчета"""
        user_data = context.user_data
        user_data.clear()
        chains = await sync_to_async(list)(TradingClient.objects.filter(is_active=True))
        if not chains:
            await update.message.reply_text("Нет доступных аптечных сетей. Обратитесь к администратору.")
            return ConversationHandler.END
        keyboard = [[chain.name] for chain in chains]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите аптечную сеть:",
            reply_markup=reply_markup
        )
        return SELECTING_CHAIN

    async def select_chain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор аптечной сети"""
        chain_name = update.message.text
        user_data = context.user_data
        try:
            chain = await sync_to_async(TradingClient.objects.get)(
                name=chain_name, 
                is_active=True
            )
            user_data['chain'] = chain
            user_data['chain_name'] = chain_name
            categories = await sync_to_async(list)(CategoryProduct.objects.all())
            keyboard = [[category.get_name_display()] for category in categories]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                "Выберите категорию товаров:",
                reply_markup=reply_markup
            )
            return SELECTING_CATEGORY
        except TradingClient.DoesNotExist:
            await update.message.reply_text("Аптечная сеть не найдена. Попробуйте еще раз.")
            return SELECTING_CHAIN

    async def select_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор категории"""
        category_display = update.message.text
        user_data = context.user_data
        try:
            all_categories = await sync_to_async(list)(CategoryProduct.objects.all())
            category = None
            for cat in all_categories:
                if cat.get_name_display() == category_display:
                    category = cat
                    break
            if not category:
                raise CategoryProduct.DoesNotExist
            user_data['category'] = category
            user_data['category_name'] = category_display
            brands = await sync_to_async(list)(
                BrandProduct.objects.filter(category=category, is_active=True)
            )
            if not brands:
                await update.message.reply_text("Нет доступных брендов для выбранной категории.")
                return ConversationHandler.END
            keyboard = [[brand.name] for brand in brands]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                "Выберите бренд:",
                reply_markup=reply_markup
            )
            return SELECTING_BRAND
        except CategoryProduct.DoesNotExist:
            await update.message.reply_text("Категория не найдена. Попробуйте еще раз.")
            return SELECTING_CATEGORY

    async def select_brand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор бренда"""
        brand_name = update.message.text
        user_data = context.user_data
        try:
            brand = await sync_to_async(BrandProduct.objects.get)(
                name=brand_name,
                category=user_data['category'],
                is_active=True
            )
            user_data['brand'] = brand
            user_data['brand_name'] = brand_name
            user_data['photos'] = []
            user_data['photo_count'] = 0
            user = await sync_to_async(User.objects.get)(telegram_id=update.effective_user.id)
            report = PhotoReport(
                user=user,
                trading_client=user_data['chain'],
                category=user_data['category'],
                brand=user_data['brand'],
                is_competitor=False
            )
            await sync_to_async(report.save)()
            user_data['report_id'] = report.id
            keyboard = [
                ["Сделать фото"],
                ["Завершить отчет"],
                ["Перейти к конкурентам"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                f"Начинаем загрузку фото для бренда {brand_name}\n\n"
                "Сделайте и отправьте до 3 фотографий,\n"
                "или перейдите к фотоотчету по конкуренту бренда\n",
                reply_markup=reply_markup
            )
            return UPLOADING_PHOTOS
        except BrandProduct.DoesNotExist:
            await update.message.reply_text("Бренд не найден. Попробуйте еще раз.")
            return SELECTING_BRAND

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка фотографий своего бренда"""
        user_data = context.user_data
        photo_count = user_data.get('photo_count', 0)
        if photo_count >= 3:
            await update.message.reply_text("✅ Максимальное количество фото (3/3) уже загружено.")
            keyboard = [
                ["Завершить отчет"],
                ["Перейти к конкурентам"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Вы можете завершить отчет или перейти к конкурентам.",
                reply_markup=reply_markup
            )
            return UPLOADING_PHOTOS
        photo_file = await update.message.photo[-1].get_file()
        photo_buffer = io.BytesIO()
        await photo_file.download_to_memory(out=photo_buffer)
        try:
            report = await sync_to_async(PhotoReport.objects.get)(id=user_data['report_id'])
            if photo_count == 0:
                await sync_to_async(report.photo_1.save)(
                    f'photo_1_{report.id}.jpg', 
                    ContentFile(photo_buffer.getvalue())
                )
            elif photo_count == 1:
                await sync_to_async(report.photo_2.save)(
                    f'photo_2_{report.id}.jpg', 
                    ContentFile(photo_buffer.getvalue())
                )
            elif photo_count == 2:
                await sync_to_async(report.photo_3.save)(
                    f'photo_3_{report.id}.jpg', 
                    ContentFile(photo_buffer.getvalue())
                )
            user_data['photo_count'] = photo_count + 1
            progress_text = f"✅ Фото {user_data['photo_count']}/3 сохранено!"
            if user_data['photo_count'] >= 3:
                keyboard = [
                    ["Завершить отчет"],
                    ["Перейти к конкурентам"]
                ]
                progress_text += "\n\n🎉 Все фото загружены!"
            else:
                keyboard = [
                    ["Сделать фото"],
                    ["Завершить отчет"],
                    ["Перейти к конкурентам"]
                ]
                progress_text += f"\nМожно добавить еще {3 - user_data['photo_count']} фото"
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(progress_text, reply_markup=reply_markup)
        except PhotoReport.DoesNotExist:
            await update.message.reply_text("❌ Ошибка: отчет не найден. Начните заново с /new_report")
            return ConversationHandler.END
        return UPLOADING_PHOTOS

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых команд в режиме загрузки фото"""
        text = update.message.text
        user_data = context.user_data
        if text == "Завершить отчет":
            return await self.finish_report(update, context)
        elif text == "Перейти к конкурентам":
            return await self.start_competitor_mode(update, context)
        elif text == "Сделать фото":
            await update.message.reply_text(
                "📸 Отправьте фото в чат. Вы можете отправить до 3 фотографий."
            )
        else:
            try:
                if 'report_id' in user_data:
                    report = await sync_to_async(PhotoReport.objects.get)(id=user_data['report_id'])
                    report.comment = text
                    await sync_to_async(report.save)()
                    await update.message.reply_text("✅ Комментарий сохранен!")
            except PhotoReport.DoesNotExist:
                await update.message.reply_text("❌ Ошибка: отчет не найден")
        return UPLOADING_PHOTOS

    async def start_competitor_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Переход в режим конкурентов"""
        user_data = context.user_data
        user_data['competitor_photos'] = []
        user_data['competitor_photo_count'] = 0
        user = await sync_to_async(User.objects.get)(telegram_id=update.effective_user.id)
        competitor_report = PhotoReport(
            user=user,
            trading_client=user_data['chain'],
            category=user_data['category'],
            brand=user_data['brand'],
            is_competitor=True
        )
        await sync_to_async(competitor_report.save)()
        user_data['competitor_report_id'] = competitor_report.id
        keyboard = [
            ["Сделать фото конкурента"],
            ["Завершить конкурентный отчет"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "📸 *Режим конкурентов*\n\n"
            "Теперь делайте фото конкурентных товаров.\n"
            "Можно загрузить до 3 фото.\n\n",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return COMPETITOR_MODE

    async def handle_competitor_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка фотографий конкурентов"""
        user_data = context.user_data
        photo_count = user_data.get('competitor_photo_count', 0)
        if photo_count >= 3:
            await update.message.reply_text("✅ Максимальное количество фото конкурентов (3) достигнуто.")
            keyboard = [["Завершить конкурентный отчет"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Вы можете завершить конкурентный отчет.",
                reply_markup=reply_markup
            )
            return COMPETITOR_MODE
        photo_file = await update.message.photo[-1].get_file()
        photo_buffer = io.BytesIO()
        await photo_file.download_to_memory(out=photo_buffer)
        try:
            report = await sync_to_async(PhotoReport.objects.get)(id=user_data['competitor_report_id'])
            if photo_count == 0:
                await sync_to_async(report.photo_1.save)(
                    f'competitor_1_{report.id}.jpg', 
                    ContentFile(photo_buffer.getvalue())
                )
            elif photo_count == 1:
                await sync_to_async(report.photo_2.save)(
                    f'competitor_2_{report.id}.jpg', 
                    ContentFile(photo_buffer.getvalue())
                )
            elif photo_count == 2:
                await sync_to_async(report.photo_3.save)(
                    f'competitor_3_{report.id}.jpg', 
                    ContentFile(photo_buffer.getvalue())
                )
            user_data['competitor_photo_count'] = photo_count + 1
            progress_text = f"✅ Фото конкурента {user_data['competitor_photo_count']}/3 сохранено!"
            if user_data['competitor_photo_count'] >= 3:
                keyboard = [["Завершить конкурентный отчет"]]
                progress_text += "\n\n🎉 Все фото конкурентов загружены!"
            else:
                keyboard = [
                    ["Сделать фото конкурента"],
                    ["Завершить конкурентный отчет"]
                ]
                progress_text += f"\nМожно добавить еще {3 - user_data['competitor_photo_count']} фото"
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(progress_text, reply_markup=reply_markup)
        except PhotoReport.DoesNotExist:
            await update.message.reply_text("❌ Ошибка: отчет конкурента не найден")
        return COMPETITOR_MODE

    async def handle_competitor_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текста в режиме конкурентов"""
        text = update.message.text
        user_data = context.user_data
        if text == "Завершить конкурентный отчет":
            return await self.finish_competitor_report(update, context)
        elif text == "Сделать фото конкурента":
            await update.message.reply_text("📸 Отправьте фото конкурента в чат")
        else:
            try:
                report = await sync_to_async(PhotoReport.objects.get)(id=user_data['competitor_report_id'])
                report.comment = text
                await sync_to_async(report.save)()
                await update.message.reply_text("✅ Комментарий к конкурентам сохранен!")
            except PhotoReport.DoesNotExist:
                await update.message.reply_text("❌ Ошибка: отчет конкурента не найден")
        return COMPETITOR_MODE

    async def finish_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Завершение основного отчета"""
        user_data = context.user_data
        try:
            report = await sync_to_async(PhotoReport.objects.get)(id=user_data['report_id'])
            photos_count = await sync_to_async(report.get_photos_count)()
            keyboard = [["📋 Новый отчет"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                f"✅ *Отчет завершен!*\n\n"
                f"📊 *Детали отчета:*\n"
                f"• Бренд: {user_data['brand_name']}\n"
                f"• Фото: {photos_count}/3\n"
                f"• Сеть: {user_data['chain_name']}\n"
                f"• Категория: {user_data['category_name']}\n\n"
                f"Нажмите кнопку ниже для создания нового отчета",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except PhotoReport.DoesNotExist:
            keyboard = [["📋 Новый отчет"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                "❌ Ошибка при завершении отчета\n"
                "Нажмите кнопку ниже для создания нового отчета",
                reply_markup=reply_markup
            )
        user_data.clear()
        return ConversationHandler.END

    async def finish_competitor_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Завершение конкурентного отчета"""
        user_data = context.user_data
        try:
            report = await sync_to_async(PhotoReport.objects.get)(id=user_data['competitor_report_id'])
            photos_count = await sync_to_async(report.get_photos_count)()
            keyboard = [["📋 Новый отчет"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                f"✅ *Конкурентный отчет завершен!*\n\n"
                f"📊 *Детали отчета:*\n"
                f"• Основной бренд: {user_data['brand_name']}\n"
                f"• Фото конкурентов: {photos_count}/3\n"
                f"• Сеть: {user_data['chain_name']}\n"
                f"• Категория: {user_data['category_name']}\n\n"
                f"Нажмите кнопку ниже для создания нового отчета",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except PhotoReport.DoesNotExist:
            keyboard = [["📋 Новый отчет"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                "❌ Ошибка при завершении конкурентного отчета\n"
                "Нажмите кнопку ниже для создания нового отчета",
                reply_markup=reply_markup
            )
        user_data.clear()
        return ConversationHandler.END

    async def handle_finish_anywhere(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка завершения отчета из любого состояния"""
        user_data = context.user_data
        if 'report_id' in user_data:
            return await self.finish_report(update, context)
        elif 'competitor_report_id' in user_data:
            return await self.finish_competitor_report(update, context)
        else:
            return await self.cancel(update, context)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции"""
        keyboard = [["📋 Новый отчет"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "❌ Операция отменена. Нажмите кнопку ниже для создания нового отчета.",
            reply_markup=reply_markup
        )
        context.user_data.clear()
        return ConversationHandler.END

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка неизвестных команд и кнопки 'Новый отчет'"""
        text = update.message.text
        if text == "📋 Новый отчет" or text == "Новый отчет":
            return await self.new_report(update, context)
        else:
            await update.message.reply_text(
                "❌ Неизвестная команда. Используйте /start для начала работы или нажмите '📋 Новый отчет' для создания отчета."
            )
