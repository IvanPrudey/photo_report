from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from constants.constants import (
    ROLE_CHOICES,
    CATEGORY_CHOICES
)


class User(AbstractUser):

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
    pass


class PhotoReport(models.Model):
    pass
