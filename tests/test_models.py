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

    def test_user_incorrect_role(self, db):
        with pytest.raises(ValidationError):
            user = User(
                telegram_id=234567890,
                username='incorrect_user',
                role='superuser'
            )
            user.full_clean()


class TestTradingClientModel:

    def test_trading_client_creation(self, test_trading_client):
        assert test_trading_client.name == 'Тестовая аптечная сеть', 'name должно иметь значение Тестовая аптечная сеть'
        assert test_trading_client.is_active is True, 'is_active должно иметь значение True'


class TestCategoryModel:

    def test_category_creation(self, test_category):
        assert test_category.name == 'ЛС', 'name должно иметь значение ЛС'
        assert test_category.get_name_display() == 'Лекарственные', 'display_name должно быть Лекарственные'

    def test_category_str_method(self, db):
        categories_data = [
            ('ЛС', 'Лекарственные'),
            ('КС', 'Косметические'),
            ('ОТС', 'Безрецептурные'),
        ]
        for code, display_name in categories_data:
            category = CategoryProduct.objects.create(name=code)
            assert str(category) == display_name, f'Для {code} должно быть представление {display_name}'
            assert category.get_name_display() == display_name

    def test_category_incorrect_choice(self, db):
        with pytest.raises(ValidationError):
            category = CategoryProduct(
                name='INCORRECT'
            )
            category.full_clean()


class TestBrandModel:

    def test_brand_creation(self, test_brand, test_category):
        assert test_brand.name == 'Тестовый бренд', 'name должно иметь значение Тестовый бренд'
        assert test_brand.category == test_category, 'Бренд должен быть связан с правильной категорией'
        assert test_brand.is_active is True, 'is_active должно иметь значение True'


class TestPhotoReportModel:

    def test_photo_report_creation_with_fixture(self, test_photo_report):
        report = test_photo_report
        assert report.user is not None
        assert report.trading_client is not None
        assert report.category is not None
        assert report.brand is not None
        assert report.is_competitor is False
        assert report.photo_1 is not None
        assert report.comment == ''
        assert report.created_at is not None

    def test_photo_report_with_all_fields(self, test_user, test_trading_client, test_category, test_brand, sample_image):
        report = PhotoReport.objects.create(
            user=test_user,
            trading_client=test_trading_client,
            category=test_category,
            brand=test_brand,
            is_competitor=True,
            photo_1=sample_image,
            photo_2=sample_image,
            photo_3=sample_image,
            comment='Тестовый комментарий'
        )
        assert report.is_competitor is True
        assert report.photo_1 is not None
        assert report.photo_2 is not None
        assert report.photo_3 is not None
        assert report.comment == 'Тестовый комментарий'
        assert report.get_photos_count() == 3

    def test_photo_report_minimal_fields(self, test_user, test_trading_client, test_category, test_brand):
        report = PhotoReport.objects.create(
            user=test_user,
            trading_client=test_trading_client,
            category=test_category,
            brand=test_brand
        )
        assert report.is_competitor is False
        assert not report.photo_1
        assert not report.photo_2
        assert not report.photo_3
        assert report.comment == ''
        assert report.get_photos_count() == 0
