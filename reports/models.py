from django.db import models
from django.contrib.auth.models import AbstractUser

from constants.constants import (
    ROLE_CHOICES
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
        auto_now_add=True,
        verbose_name='Последняя активность'
    )
