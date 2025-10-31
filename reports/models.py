from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

from constants.constants import (
    ROLE_CHOICES,
    CATEGORY_CHOICES
)
from .upload_paths import photo_upload_path


class User(AbstractUser):

    groups = None
    user_permissions = None
    telegram_id = models.BigIntegerField(
        unique=True,
        blank=True,
        null=True,
        verbose_name='ID в Telegram',
        help_text='Уникальный идентификатор пользователя в Telegram'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Подтвержден'
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Последняя активность',
        help_text='Время последней активности пользователя в боте'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    def update_activity(self):
        User.objects.filter(pk=self.pk).update(last_activity=timezone.now())


class TradingClient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название сети'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )

    class Meta:
        verbose_name = 'Аптечная сеть'
        verbose_name_plural = 'Аптечные сети'
        ordering = ['name']

    def __str__(self):
        return self.name


class CategoryProduct(models.Model):
    name = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        unique=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


class BrandProduct(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Название бренда'
    )
    category = models.ForeignKey(
        CategoryProduct,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='brands'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.category})'


class PhotoReport(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='reports'
    )
    trading_client = models.ForeignKey(
        TradingClient,
        on_delete=models.CASCADE,
        verbose_name='Аптечная сеть'
    )
    category = models.ForeignKey(
        CategoryProduct,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    brand = models.ForeignKey(
        BrandProduct,
        on_delete=models.CASCADE,
        verbose_name='Бренд'
    )
    is_competitor = models.BooleanField(
        default=False,
        verbose_name='Отчет по конкуренту'
    )
    photo_1 = models.ImageField(
        upload_to=photo_upload_path,
        verbose_name='Фото 1',
        null=True,
        blank=True
    )
    photo_2 = models.ImageField(
        upload_to=photo_upload_path,
        verbose_name='Фото 2',
        null=True,
        blank=True
    )
    photo_3 = models.ImageField(
        upload_to=photo_upload_path,
        verbose_name='Фото 3',
        null=True,
        blank=True
    )
    comment = models.TextField(
        blank=True, 
        verbose_name='Комментарий'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Фотоотчет'
        verbose_name_plural = 'Фотоотчеты'
        ordering = ['-created_at']

    def __str__(self):
        if self.is_competitor:
            return f'Отчет по конкуренту - {self.trading_client} - {self.category}'
        else:
            return f'Отчет по {self.brand} - {self.trading_client}'

    def get_photos_count(self):
        count = 0
        if self.photo_1:
            count += 1
        if self.photo_2:
            count += 1
        if self.photo_3:
            count += 1
        return count

    def clean(self):
        if not self.brand:
            raise ValidationError('Бренд должен быть выбран')
