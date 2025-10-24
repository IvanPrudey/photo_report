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