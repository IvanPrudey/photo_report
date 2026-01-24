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
        username='test_user',
        first_name='Test',
        last_name='User',
        role='user'
    )
