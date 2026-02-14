import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from reports.models import (
    BrandProduct,
    CategoryProduct,
    PhotoReport,
    TradingClient,
    User
)


class TestUserModel:

    def test_user_creation_with_correct_fields(self, test_user):
        assert test_user.telegram_id == 123456789, 'telegram_id должно иметь значение 123456789'
        assert test_user.username == 'ivanov_ivan', 'username должно иметь значение ivanov_ivan'
        assert test_user.first_name == 'Ivanov', 'first_name должно иметь значение Ivanov'
        assert test_user.last_name == 'Ivan', 'last_name должно иметь значение Ivan'
        assert test_user.role == 'user', 'role должно иметь значение user'
        assert test_user.is_verified is False, 'is_verified должно иметь значение False'


class TestTradingClientModel:

    def test_trading_client_creation(self, test_trading_client):
        assert test_trading_client.name == 'Тестовая аптечная сеть', 'name должно иметь значение Тестовая аптечная сеть'
        assert test_trading_client.is_active is True, 'is_active должно иметь значение True'


class TestCategoryModel:

    def test_category_creation(self, test_category):
        assert test_category.name == 'ЛС', 'name должно иметь значение ЛС'


class TestBrandModel:


class PhotoReportModel:
    pass