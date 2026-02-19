import os
import uuid
from django.utils import timezone


def photo_upload_path(instance, filename):
    if instance.created_at:
        year = instance.created_at.year
        month = instance.created_at.month
    else:
        now = timezone.now()
        year = now.year
        month = now.month

    safe_chain_name = ''.join(
        c for c in instance.trading_client.name if c.isalnum() or c in (' ', '-', '_')
    ).rstrip()
    safe_category_name = ''.join(
        c for c in instance.category.name if c.isalnum() or c in (' ', '-', '_')
    ).rstrip()
    if instance.is_competitor:
        brand_folder = os.path.join(instance.brand.name, 'competitor')
    else:
        brand_folder = instance.brand.name
    file_ext = os.path.splitext(filename)[1]
    unique_filename = f'{uuid.uuid4().hex}{file_ext}'
    return os.path.join(
        'photo_reports',
        str(year),
        f'{month:02d}',
        safe_chain_name,
        safe_category_name,
        brand_folder,
        unique_filename
    )