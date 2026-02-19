import os
import sys
import django
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from reports.models import (
    BrandProduct,
    CategoryProduct,
    PhotoReport,
    TradingClient,
    User
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_report.settings')
django.setup()


@pytest.fixture
def test_user(db):
    return User.objects.create(
        telegram_id=123456789,
        username='ivanov_ivan',
        first_name='Ivanov',
        last_name='Ivan',
        role='user'
    )


@pytest.fixture
def test_trading_client(db):
    return TradingClient.objects.create(
        name='Тестовая аптечная сеть',
        is_active=True
    )


@pytest.fixture
def test_category(db):
    return CategoryProduct.objects.create(
        name='ЛС'
    )


@pytest.fixture
def test_brand(db, test_category):
    return BrandProduct.objects.create(
        name='Тестовый бренд',
        category=test_category,
        is_active=True
    )


@pytest.fixture
def sample_image():
    return SimpleUploadedFile(
        name='test_photo.jpg',
        content=b'fake image content',
        content_type='image/jpeg'
    )


@pytest.fixture
def test_photo_report(db, test_user, test_trading_client, test_category, test_brand, sample_image):
    report = PhotoReport.objects.create(
        user=test_user,
        trading_client=test_trading_client,
        category=test_category,
        brand=test_brand,
        is_competitor=False,
        photo_1=sample_image
    )
    yield report
    if report.photo_1:
        report.photo_1.delete(save=False)
